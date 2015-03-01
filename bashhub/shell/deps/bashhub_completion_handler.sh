_bashhub_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _BASHHUB_COMPLETE=complete $1 ) )
    return 0
}

complete -F _bashhub_completion -o default bashhub;
