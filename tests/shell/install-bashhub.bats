#!/usr/bin/env bats

setup() {
  bashhub_install_test="true"
  source "${BATS_TEST_DIRNAME}"/../../install-bashhub.sh
}

@test "detect_shell_type should detect our default shell" {
  BASH_VERSION=1
  run 'detect_shell_type'
  [[ $status == 0 ]]
  [[ "$output" == "bash" ]]

  ZSH_VERSION=1
  # Check to detect zs
  run 'detect_shell_type'
  [[ $status == 0 ]]
  [[ "$output" == "zsh" ]]
}

@test "check_dependencies should fail if we don't have our dependencies" {
  unset BASH_VERSION
  run 'check_dependencies'
  [[ $status == 1 ]]
  [[ "$output" == *"Bashhub only supports"* ]]

  BASH_VERSION=1
  run 'check_dependencies'
  [[ $status == 0 ]]
}

@test "get_and_check_python_version should find python3 first" {
  # Mock up some fake responses here.
  python3.7() { return 1; }
  python3.6() { return 1; }
  python3.5() { return 1; }
  python3() { return 0; }
  python() { return 1; }

  run 'get_and_check_python_version'
  [[ $status == 0 ]]
  [[ "$output" == "python3" ]]

  # Should find 3.5
  python3.5() { return 0; }
  run 'get_and_check_python_version'
  [[ $status == 0 ]]
  [[ "$output" == "python3.5" ]]
}

@test "get_and_check_python_version should find different python versions" {
  # Mock up some fake responses here.

  python3() { return 1; }
  python3.7() { return 1; }
  python3.6() { return 1; }
  python3.5() { return 1; }
  python() { return 1;}
  python2.7() { return 0; }

  run 'get_and_check_python_version'
  [[ $status == 0 ]]
  [[ "$output" == "python2.7" ]]

  # Should find the default installation if no others.
  python() { return 0; }

  run 'get_and_check_python_version'
  [[ $status == 0 ]]
  [[ "$output" == "python" ]]

}

@test "get_and_check_python_version should fail if there's no valid python versions" {
  # Mock up which to not work for anything.
  type() { return 1; }

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
