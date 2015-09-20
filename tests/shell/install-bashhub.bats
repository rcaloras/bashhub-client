#!/usr/bin/env bats

setup() {
  bashhub_install_test="true"
  source "${BATS_TEST_DIRNAME}"/../../install-bashhub.sh
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

@test "get_and_check_python_version should find the default python version" {
  run 'get_and_check_python_version'
  [[ $status == 0 ]]
  [[ "$output" == "python" ]]
}

@test "get_and_check_python_version should find python26" {
  # Mock up some fake responses here.
  which() { echo "some-path"; }
  python() { return 1; }
  python2() { return 1; }
  python26() { return 0; }

  run 'get_and_check_python_version'
  [[ $status == 0 ]]
  [[ "$output" == "python26" ]]
}

@test "get_and_check_python_version should fail if there's no valid python versions" {
  # Mock up which to not work for anything.
  which() { return 1; }

  run 'get_and_check_python_version'
  [[ $status == 1 ]]
}

@test "download_and_install_env should succeed" {
  if [[ -z $functional_test ]]; then
    skip "skipping functional test"
  fi

  cd "$BATS_TMPDIR"
  run 'download_and_install_env'
  [[ $status == 0 ]]
  [[ -e env ]]
}



