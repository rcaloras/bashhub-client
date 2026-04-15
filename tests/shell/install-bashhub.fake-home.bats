#!/usr/bin/env bats

setup() {
  bashhub_install_test="true"
  setup_fake_home_dir
  source "${BATS_TEST_DIRNAME}"/../../install-bashhub.sh
}

setup_fake_home_dir() {
  rm -rf "${BATS_TEST_DIRNAME}/test_home"
  mkdir -p "${BATS_TEST_DIRNAME}/test_home"
  export HOME="${BATS_TEST_DIRNAME}/test_home"
  cd "$HOME"
  echo "# This is a test bashrc" >> .bashrc
  echo "# This is a test zshrc" >> .zshrc
}

teardown() {
  rm -rf "${BATS_TEST_DIRNAME}/test_home"
}

install_bashhub() {
  bash "${BATS_TEST_DIRNAME}"/../install-bashhub.sh
}

@test "install_hooks_for_shell should install for bash" {
  run install_hooks_for_shell
  [[ $status == 0 ]]
  in_profile=$(grep -q 'bashhub.sh' "$HOME/.bashrc"; echo $?;)
  [[ "$in_profile" == 0 ]]

  run install_hooks_for_shell
  [[ $status == 0 ]]
  hook_count=$(grep -c 'source ~/.bashhub/bashhub.sh' "$HOME/.bashrc")
  [[ "$hook_count" == 1 ]]
}

@test "install_hooks_for_shell should install for zsh" {
  export ZSH_VERSION=1
  run install_hooks_for_shell
  [[ $status == 0 ]]
  in_profile=$(grep -q 'bashhub.zsh' "$HOME/.zshrc"; echo $?;)
  [[ "$in_profile" == 0 ]]

  run install_hooks_for_shell
  [[ $status == 0 ]]
  hook_count=$(grep -c 'source ~/.bashhub/bashhub.zsh' "$HOME/.zshrc")
  [[ "$hook_count" == 1 ]]
}

@test "install_hooks_for_shell should fail for unsupported" {
  unset BASH_VERSION
  run install_hooks_for_shell
  [[ $status == 1 ]]
}

@test "generate .bash_profile and .bashrc and link them" {
  rm "$HOME/.bashrc"
  rm "$HOME/.zshrc"
  run generate_bash_config_file
  [[ $status == 0 ]]
  [[ -f "$HOME/.bashrc"  ]]
  [[ -f "$HOME/.bash_profile" ]]
  # Should source .bashrc in .bash_profile
  in_profile=$(grep -q 'source ~/.bashrc' "$HOME/.bash_profile"; echo $?;)
  [[ "$in_profile" == 0 ]]
}

@test "check_already_installed should preserve existing config" {
  mkdir -p "$HOME/.bashhub"
  echo "access_token = test" > "$HOME/.bashhub/config"

  run check_already_installed
  [[ $status == 0 ]]
  [[ -f "$backup_config" ]]
  grep -q "access_token = test" "$backup_config"
  [[ ! -d "$HOME/.bashhub" ]]
}

@test "check_already_installed should not create bashhub directory" {
  rm -rf "$HOME/.bashhub"

  run check_already_installed
  [[ $status == 0 ]]
  [[ ! -d "$HOME/.bashhub" ]]
}
