compdef -d 'search.py'

function _search_py() {
  SUFFIX="${SUFFIX# }"
  compset -q
  compset -P '*[^a-zA-Z0-9_]'
  compset -S '[^a-zA-Z0-9_]*'

  compadd -M 'b:=*' -- $("$1" "${QIPREFIX} ${IPREFIX}")
}

setopt COMPLETE_IN_WORD
setopt NO_ALWAYS_TO_END

script_dir="$(dirname "${0:A}")"

compdef "_search_py ${script_dir}/comp_helper.py" 'search.py'
