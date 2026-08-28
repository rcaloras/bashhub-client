#!/usr/bin/env bats

setup() {
  bashhub_install_test="true"
  unset UV_TOOL_LIST_OUTPUT
  unset bashhub_version
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

@test "install_or_upgrade_bashhub_package should install the latest unpinned bashhub" {
  UV_COMMAND_LOG="$BATS_TMPDIR/uv.log"
  export UV_COMMAND_LOG

  uv() {
    echo "$*" >> "$UV_COMMAND_LOG"
  }

  run install_or_upgrade_bashhub_package uv
  [[ $status == 0 ]]
  [[ "$(cat "$UV_COMMAND_LOG")" == *"python install 3.13 --quiet"* ]]
  [[ "$(cat "$UV_COMMAND_LOG")" == *"tool install --python 3.13 --reinstall bashhub --quiet"* ]]
}

@test "install_or_upgrade_bashhub_package should replace a pinned install with latest" {
  UV_COMMAND_LOG="$BATS_TMPDIR/uv.log"
  export UV_COMMAND_LOG

  uv() {
    echo "$*" >> "$UV_COMMAND_LOG"
  }

  run install_or_upgrade_bashhub_package uv
  [[ $status == 0 ]]
  [[ "$(cat "$UV_COMMAND_LOG")" == *"python install 3.13 --quiet"* ]]
  [[ "$(cat "$UV_COMMAND_LOG")" == *"tool install --python 3.13 --reinstall bashhub --quiet"* ]]
}

@test "install_or_upgrade_bashhub_package should reinstall requested version" {
  UV_COMMAND_LOG="$BATS_TMPDIR/uv.log"
  bashhub_version="3.0.4"
  export UV_COMMAND_LOG

  uv() {
    echo "$*" >> "$UV_COMMAND_LOG"
  }

  run install_or_upgrade_bashhub_package uv
  [[ $status == 0 ]]
  [[ "$(cat "$UV_COMMAND_LOG")" == *"python install 3.13 --quiet"* ]]
  [[ "$(cat "$UV_COMMAND_LOG")" == *"tool install --python 3.13 --reinstall bashhub==3.0.4 --quiet"* ]]
}
