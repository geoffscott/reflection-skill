#!/bin/bash

###############################################################################
# reflection-skill: Import Script
# 
# Scans a source markdown vault, validates entries, and imports them into
# reflection/entries/ with standardized frontmatter.
#
# Usage:
#   ./import-script.sh /path/to/vault
#   ./import-script.sh  (interactive: prompts for path)
#
###############################################################################

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"
WORKSPACE_ROOT="$(dirname "$(dirname "$(dirname "$SKILL_ROOT")")")"

# Target directories
ENTRIES_DIR="$SKILL_ROOT/entries"
ANNOTATIONS_DIR="$SKILL_ROOT/annotations"
METADATA_FILE="$SKILL_ROOT/metadata.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global counters
declare -g -A files_by_date
declare -g total_files=0
declare -g total_words=0
declare -g errors=0
declare -g skipped=0

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Parse a date from filename (YYYY-MM-DD) or return empty if not found
parse_date_from_filename() {
    local filename="$1"
    if [[ "$filename" =~ ^([0-9]{4})-([0-9]{2})-([0-9]{2}) ]]; then
        echo "${BASH_REMATCH[1]}-${BASH_REMATCH[2]}-${BASH_REMATCH[3]}"
    fi
}

# Get file modification date safely
get_file_date() {
    local filepath="$1"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS: use -f '%SB' for birth time
        stat -f '%SB' "$filepath" 2>/dev/null | sed 's/ /T/g' | cut -d'T' -f1
    else
        # Linux: use -c '%y' for modification time, extract date
        stat -c '%y' "$filepath" 2>/dev/null | cut -d' ' -f1
    fi
}

# Infer date: try filename first, fall back to file creation date
infer_date() {
    local filepath="$1"
    local filename=$(basename "$filepath")
    
    # Try parsing from filename (YYYY-MM-DD.md)
    local date_from_name=$(parse_date_from_filename "$filename")
    if [[ -n "$date_from_name" ]]; then
        echo "$date_from_name"
        return 0
    fi
    
    # Fall back to file modification date
    local file_date=$(get_file_date "$filepath")
    if [[ -n "$file_date" ]]; then
        echo "$file_date"
        return 0
    fi
}

# Determine source type (daily vs craft archive)
determine_source_type() {
    local filepath="$1"
    if [[ "$filepath" =~ /Archive/Craft ]]; then
        echo "craft_archive"
    else
        echo "markdown"
    fi
}

# Count words in a file
count_words() {
    local filepath="$1"
    wc -w < "$filepath" 2>/dev/null | tr -d ' ' || echo "0"
}

# Create frontmatter for entry
create_frontmatter() {
    local date="$1"
    local source="$2"
    local length="$3"
    local original_filename="$4"
    
    cat <<EOF
---
date: $date
imported_from: $source
length_words: $length
EOF
    
    if [[ -n "$original_filename" ]]; then
        echo "original_filename: $original_filename"
    fi
    
    echo "---"
}

# Process a single file
process_file() {
    local filepath="$1"
    [[ ! -f "$filepath" ]] && return
    
    local filename=$(basename "$filepath")
    local date=$(infer_date "$filepath")
    
    if [[ -z "$date" ]]; then
        log_warning "Could not infer date for: $filename"
        ((errors++))
        return
    fi
    
    local source_type=$(determine_source_type "$filepath")
    local word_count=$(count_words "$filepath")
    ((total_words += word_count))
    
    local target_file="$ENTRIES_DIR/${date}.md"
    
    # Get timestamp for section header
    local timestamp
    if [[ "$OSTYPE" == "darwin"* ]]; then
        timestamp=$(stat -f '%Sm' -t '%H:%M:%S' "$filepath" 2>/dev/null || echo "00:00:00")
    else
        timestamp=$(stat -c '%y' "$filepath" 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1 || echo "00:00:00")
    fi
    
    if [[ -f "$target_file" ]]; then
        # Append to existing entry
        {
            echo ""
            echo "## $timestamp — $filename"
            cat "$filepath"
        } >> "$target_file"
        ((skipped++))
    else
        # Create new entry file with frontmatter
        {
            create_frontmatter "$date" "$source_type" "$word_count" "$filename"
            echo ""
            cat "$filepath"
        } > "$target_file"
        ((total_files++))
    fi
    
    files_by_date["$date"]=1
}

###############################################################################
# Main Import Logic
###############################################################################

main() {
    # Get source directory
    local source_dir="${1:-}"
    
    if [[ -z "$source_dir" ]]; then
        echo "Enter path to your markdown vault (e.g., /Users/geoff/Obsidian/Personal):"
        read -r source_dir
    fi
    
    # Validate source directory
    if [[ ! -d "$source_dir" ]]; then
        log_error "Source directory not found: $source_dir"
        exit 1
    fi
    
    log_info "Scanning source directory: $source_dir"
    
    # Create target directories if they don't exist
    mkdir -p "$ENTRIES_DIR"
    mkdir -p "$ANNOTATIONS_DIR"
    
    # Process daily journal entries
    if [[ -d "$source_dir/Journal" ]]; then
        log_info "Processing daily entries..."
        
        for filepath in "$source_dir"/Journal/*.md; do
            process_file "$filepath"
            
            # Progress indicator every 20 files
            if (( total_files % 20 == 0 )); then
                log_info "Processed $total_files files..."
            fi
        done
    fi
    
    # Process Craft reflections
    if [[ -d "$source_dir/Archive/Craft/My Space/Journal" ]]; then
        log_info "Processing craft reflections..."
        
        # Use while + process substitution to avoid subshell issues
        while IFS= read -r -d '' filepath; do
            process_file "$filepath"
        done < <(find "$source_dir/Archive/Craft/My Space/Journal" -type f -name "*.md" -print0)
    fi
    
    # Create metadata.json
    local import_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local earliest=$(printf '%s\n' "${!files_by_date[@]}" | sort | head -1)
    local latest=$(printf '%s\n' "${!files_by_date[@]}" | sort | tail -1)
    
    cat > "$METADATA_FILE" <<EOF
{
  "last_import": "$import_date",
  "source_directory": "$source_dir",
  "total_files_imported": $total_files,
  "total_entries_created": ${#files_by_date[@]},
  "total_words": $total_words,
  "date_range": {
    "earliest": "$earliest",
    "latest": "$latest"
  },
  "errors": $errors,
  "appended_to_existing": $skipped
}
EOF
    
    # Report summary
    echo ""
    log_success "Import complete!"
    echo ""
    echo -e "${BLUE}=== Import Summary ===${NC}"
    echo "Files imported:        $total_files"
    echo "Entries created:       ${#files_by_date[@]}"
    echo "Total words:           $total_words"
    echo "Date range:            $earliest to $latest"
    if [[ $errors -gt 0 ]]; then
        echo -e "${RED}Errors:                $errors${NC}"
    fi
    if [[ $skipped -gt 0 ]]; then
        echo "Appended to existing:  $skipped"
    fi
    echo ""
    echo "Location: $ENTRIES_DIR"
    echo "Metadata: $METADATA_FILE"
}

main "$@"
