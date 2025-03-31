#!/bin/bash
set -e

BASEDIR="$(realpath "$(dirname "$0")/..")"
cd "$BASEDIR/.git/hooks"

cat << 'EOF' > pre-commit
#!/bin/bash
set -e

BASEDIR="$(realpath "$(dirname "$0")/../..")"
$BASEDIR/bin/pre-commit.sh
EOF

chmod +x pre-commit