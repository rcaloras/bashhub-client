#!/usr/bin/env bats

setup() {
  BH_HOME_DIRECTORY="$BATS_TMPDIR"
  touch "$BATS_TMPDIR/.config"
  source "${BATS_TEST_DIRNAME}"/../../bashhub/shell/deps/lib-bashhub.sh
}

teardown() {
  if [[ -f "${BATS_TMPDIR}/log.txt" ]]; then
    rm "${BATS_TMPDIR}/log.txt"
  fi
}

@test "contains_element should check if an element exists in an array" {

  array=("one" "two" "three")

  # Should find an element
  run contains_element "one" "${array[@]}"
  [[ $status == 0 ]]

  # Should not find an element
  run contains_element "four" "${array[@]}"
  [[ $status == 1 ]]

}


@test "__bh_precmd should check if our home directory exists" {
  BH_HOME_DIRECTORY="$non-existent"
  __BH_SAVE_COMMAND="something to save"

  __bh_process_command() {
    echo "shouldn't be logged" > "${BATS_TMPDIR}/log.txt"
  }

  run '__bh_precmd'

  BH_HOME_DIRECTORY="$BATS_TMPDIR"

  __bh_process_command() {
    echo "some output"
  }

  run '__bh_precmd'

  [[ $status == 0 ]]
  [[ -s "${BATS_TMPDIR}/log.txt" ]]
  logged=$(head -n 1 "${BATS_TMPDIR}/log.txt")
  # We should only have logged 'some output' since our Home directory exists
  [[ "$logged" == "some output" ]]
}

@test "__bh_precmd should only call process command if we have a command to save" {
  skip "Failing inconsistently on travis. Need to debug, skipping for now"

  BH_HOME_DIRECTORY="$BATS_TMPDIR"

  __bh_process_command() {
    echo "some output"
  }
  run '__bh_precmd'

  [[ ! -e "${BATS_TMPDIR}/log.txt" ]]

  # If we have a command it should save it
  __BH_SAVE_COMMAND="something to save"

  __bh_precmd
  [[ -e "${BATS_TMPDIR}/log.txt" ]]

  # mock saving by having it write to output file
  logged=$(head -n 1 "${BATS_TMPDIR}/log.txt")
  [[ "$logged" == "some output" ]]

  # __BH_SAVE_COMMAND should get unset
  [[ -z "$__BH_SAVE_COMMAND" ]]
}


