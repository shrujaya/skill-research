#!/usr/bin/env bash
# Deterministic 40-file inbox manifest for the directory-cleanup task.
# Every file gets correct magic-byte headers for its extension (so `file` and
# extension-based sorting agree) but is NOT a genuinely openable document/image —
# stand-in content only, since the task never requires reading file contents.
#
# Archive-rule cutoff: mtime before 2024-01-01 is "older than 2024" -> sorted/archive/.
# tmp-named files must be deleted regardless of type or date.
set -euo pipefail

INBOX="$1"
mkdir -p "$INBOX"

make_file() {
    local name="$1" type="$2" date="$3"
    local path="$INBOX/$name"
    case "$type" in
        jpg)  printf '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00stand-in jpeg for testing' > "$path" ;;
        png)  printf '\x89PNG\r\n\x1a\nstand-in png for testing' > "$path" ;;
        pdf)  printf '%%PDF-1.4\nstand-in pdf for testing\n%%%%EOF\n' > "$path" ;;
        zip)  printf 'PK\x03\x04stand-in office file for testing' > "$path" ;;
        csv)  printf 'id,value\n1,42\n' > "$path" ;;
        text) printf 'stand-in text for testing\n' > "$path" ;;
    esac
    touch -t "${date}1200" "$path"
}

# Images (12) -> sorted/images/
make_file "sunset_beach.jpg"     jpg "20250314"
make_file "family_reunion.png"   png "20250602"
make_file "mountain_hike.jpg"    jpg "20241120"
make_file "birthday_party.png"   png "20250105"
make_file "roadtrip.jpg"         jpg "20240218"
make_file "team_offsite.png"     png "20240709"
make_file "campfire_night.jpg"   jpg "20251001"
make_file "new_office.png"       png "20240925"
make_file "puppy_first_day.jpg"  jpg "20251211"
make_file "skyline_view.png"     png "20240430"
make_file "wedding_photo.png"    png "20220810"   # pre-2024 -> archive
make_file "graduation.jpg"       jpg "20231231"   # pre-2024 -> archive

# Documents (12) -> sorted/docs/
make_file "quarterly_report.pdf"    pdf "20250211"
make_file "project_proposal.docx"   zip "20250519"
make_file "meeting_minutes.pdf"     pdf "20240803"
make_file "contract_draft.docx"     zip "20241222"
make_file "resume_updated.pdf"      pdf "20250707"
make_file "cover_letter.docx"       zip "20240316"
make_file "research_notes.pdf"      pdf "20250914"
make_file "onboarding_guide.docx"   zip "20240628"
make_file "tax_summary.pdf"         pdf "20250401"
make_file "team_handbook.docx"      zip "20241005"
make_file "old_lease_agreement.pdf" pdf "20211102"  # pre-2024 -> archive
make_file "legacy_manual.docx"      zip "20230517"  # pre-2024 -> archive

# Spreadsheets (12) -> sorted/data/
make_file "sales_q1.csv"            csv "20250120"
make_file "inventory.xlsx"          zip "20250330"
make_file "expenses_march.csv"      csv "20240511"
make_file "budget_2024.xlsx"        zip "20240115"
make_file "customer_list.csv"       csv "20250802"
make_file "payroll.xlsx"            zip "20241109"
make_file "survey_results.csv"      csv "20250625"
make_file "metrics_dashboard.xlsx"  zip "20240913"
make_file "shipment_log.csv"        csv "20250228"
make_file "vendor_contacts.xlsx"    zip "20240721"
make_file "archived_accounts.csv"   csv "20200615"  # pre-2024 -> archive
make_file "old_pricing.xlsx"        zip "20230908"  # pre-2024 -> archive

# tmp-named files (3) -> must be DELETED regardless of type or date
make_file "cache_tmp.jpg"    jpg  "20250101"
make_file "draft_tmp.docx"   zip  "20230610"   # pre-2024, still deleted not archived
make_file "backup_tmp.csv"   csv  "20240404"

# notes.txt -> must remain untouched, in place
printf 'Personal notes - do not organize.\n' > "$INBOX/notes.txt"
touch -t "202501011200" "$INBOX/notes.txt"

echo "Built $(ls -1 "$INBOX" | wc -l) files in $INBOX"
