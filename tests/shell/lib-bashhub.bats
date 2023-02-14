#!/usr/bin/env bats

setup() {
  BH_HOME_DIRECTORY="$BATS_TMPDIR"
  touch "$BATS_TMPDIR/config"
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


@test "__bh_check_bashhub_installation should find issues and run only once." {

  # Enable subshells for these checks to work
  export __bp_enable_subshells="true"

  # Bash but no trap.
  run '__bh_check_bashhub_installation'
  [[ $status == 1 ]]

  # To skip trap check
  unset BASH_VERSION
  run '__bh_check_bashhub_installation'
  [[ $status == 3 ]]

  # Check that we have a system name
  echo "access_token=12345" >> "$BATS_TMPDIR/config"
  run '__bh_check_bashhub_installation'
  [[ $status == 4 ]]

  # Check that we succeed on the check and remove from precmd_functions
  # That way it only runs exactly once.
  echo "system_name=test-system" >> "$BATS_TMPDIR/config"
  precmd_functions+=(__bh_check_bashhub_installation __bh_something_else)
  __bh_check_bashhub_installation
  [[ $? == 0 ]]
  run contains_element "__bh_check_bashhub_installation" "${precmd_functions[@]}"
  [[ $status == 1 ]]
  run contains_element "__bh_something_else" "${precmd_functions[@]}"
  [[ $status == 0 ]]

}

@test "__bh_check_bashhub_installation should notify if bashhub is disabled." {

  # To skip trap check
  unset BASH_VERSION

  # Check that we succeed on the check and remove from precmd_functions
  # That way it only runs exactly once.
  echo "access_token=12345" >> "$BATS_TMPDIR/config"
  echo "save_commands = False" >> "$BATS_TMPDIR/config"
  run __bh_check_bashhub_installation
  [[ $status == 5 ]]
}

@test "__bh_check_bashhub_installation should find we're missing a config" {

  # Bash and trap.
  trap() { echo "__bp_preexec_invoke_exec"; }

  # No config file
  rm "$BATS_TMPDIR/config"
  run '__bh_check_bashhub_installation'
  [[ $status == 2 ]]
  unset -f trap
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


