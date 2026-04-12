#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAMPLES_DIR="${SAMPLES_DIR:-$ROOT_DIR/samples/documents}"

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "Missing required file: $path" >&2
    exit 1
  fi
}

request_json() {
  local method="$1"
  local url="$2"
  local output_file="$3"
  shift 3

  local status
  status="$(curl -sS -o "$output_file" -w "%{http_code}" -X "$method" "$url" "$@")"
  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    echo "Request failed: $method $url -> HTTP $status" >&2
    cat "$output_file" >&2
    echo >&2
    exit 1
  fi
}

json_get() {
  local file="$1"
  local expr="$2"
  python3 - "$file" "$expr" <<'PY'
import json
import sys

path = sys.argv[2].split(".")
value = json.loads(open(sys.argv[1], encoding="utf-8").read())
for key in path:
    if key.isdigit():
        value = value[int(key)]
    else:
        value = value[key]
if isinstance(value, (dict, list)):
    print(json.dumps(value, ensure_ascii=False))
elif value is None:
    print("null")
else:
    print(value)
PY
}

print_summary() {
  local label="$1"
  local file="$2"
  python3 - "$label" "$file" <<'PY'
import json
import sys

label = sys.argv[1]
payload = json.loads(open(sys.argv[2], encoding="utf-8").read())
flags = payload.get("validation_flags") or []
extraction = payload.get("extraction") or {}
normalized = extraction.get("normalized_extraction_json") or {}

print(f"{label}:")
print(f"  status={payload.get('status')}")
print(f"  document_type={payload.get('document_type')}")
print(f"  processing_status={payload.get('processing_status')}")
print(f"  pages={payload.get('page_count')}")
print(f"  ocr_confidence={payload.get('ocr_confidence')}")
print(f"  extraction_confidence={payload.get('extraction_confidence')}")
print(f"  validation_flags={len(flags)}")
print(f"  extracted_keys={','.join(sorted(normalized.keys())) if normalized else 'none'}")
PY
}

assert_document_detail() {
  local label="$1"
  local file="$2"
  python3 - "$label" "$file" <<'PY'
import json
import sys

label = sys.argv[1]
payload = json.loads(open(sys.argv[2], encoding="utf-8").read())

if payload.get("page_count", 0) < 1:
    raise SystemExit(f"{label}: expected page_count >= 1")
if payload.get("ocr_confidence") is None:
    raise SystemExit(f"{label}: missing ocr_confidence")
if payload.get("document_type") == "unknown":
    raise SystemExit(f"{label}: classifier returned unknown")
if not payload.get("extraction"):
    raise SystemExit(f"{label}: missing extraction payload")

normalized = payload["extraction"].get("normalized_extraction_json") or {}
if not normalized:
    raise SystemExit(f"{label}: normalized extraction is empty")
PY
}

main() {
  require_file "$SAMPLES_DIR/id_card_sample.png"
  require_file "$SAMPLES_DIR/payslip_sample.png"
  require_file "$SAMPLES_DIR/bank_statement_sample.pdf"

  local tmp_dir=""
  tmp_dir="$(mktemp -d)"
  trap 'if [[ -n "${tmp_dir:-}" ]]; then rm -rf "$tmp_dir"; fi' EXIT

  echo "Creating application via $BASE_URL"
  request_json "POST" "$BASE_URL/applications" "$tmp_dir/application.json" \
    -H "Content-Type: application/json" \
    --data '{"applicant_name":"Local E2E Verification"}'
  local application_id
  application_id="$(json_get "$tmp_dir/application.json" "id")"
  echo "Application ID: $application_id"

  local labels=("id_card" "payslip" "bank_statement")
  local files=(
    "$SAMPLES_DIR/id_card_sample.png"
    "$SAMPLES_DIR/payslip_sample.png"
    "$SAMPLES_DIR/bank_statement_sample.pdf"
  )

  local index
  for index in "${!labels[@]}"; do
    local label="${labels[$index]}"
    local source_file="${files[$index]}"
    local upload_file="$tmp_dir/${label}_upload.json"
    local process_file="$tmp_dir/${label}_process.json"
    local detail_file="$tmp_dir/${label}_detail.json"

    echo
    echo "Uploading $label from $source_file"
    request_json "POST" "$BASE_URL/applications/$application_id/documents" "$upload_file" \
      -F "file=@$source_file"

    local document_id
    document_id="$(json_get "$upload_file" "document_id")"
    echo "Document ID: $document_id"

    echo "Processing $label"
    request_json "POST" "$BASE_URL/documents/$document_id/process" "$process_file"

    echo "Fetching detail for $label"
    request_json "GET" "$BASE_URL/documents/$document_id" "$detail_file"

    assert_document_detail "$label" "$detail_file"
    print_summary "$label" "$detail_file"
  done

  echo
  echo "Local end-to-end verification passed."
}

main "$@"
