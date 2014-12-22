#!/usr/bin/env bats

setup() {
  bashhub_install_test="true"
  source "${BATS_TEST_DIRNAME}"/../install-bashhub.sh
}

@test "detect_shell_type should detect our default shell" {
  SHELL=$(which bash)
  run 'detect_shell_type'
  [[ $status == 0 ]]
  [[ "$output" == "bash" ]]

  # Check to detect zsh
  SHELL=$(which zsh)
  run 'detect_shell_type'
  [[ $status == 0 ]]
  [[ "$output" == "zsh" ]]
}

@test "check_dependencies should fail if we don't have our dependencies" {
  unset SHELL
  run 'check_dependencies'
  [[ $status == 1 ]]
  [[ "$output" == *"Bashhub only supports"* ]]

  SHELL=$(which bash)
  run 'check_dependencies'
  [[ $status == 0 ]]
}
