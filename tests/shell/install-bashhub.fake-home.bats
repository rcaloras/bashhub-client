#!/usr/bin/env bats

setup() {
  bashhub_install_test="true"
  setup_fake_home_dir
  source "${BATS_TEST_DIRNAME}"/../../install-bashhub.sh
}

setup_fake_home_dir() {
  mkdir "${BATS_TEST_DIRNAME}/test_home"
  HOME="${BATS_TEST_DIRNAME}/test_home"
  cd "$HOME"
  echo "# This is a test bashrc" >> .bashrc
  echo "# This is a test zshrc" >> .zshrc
}

teardown() {
  rm -r "${BATS_TEST_DIRNAME}/test_home"
}

install_bashhub() {
  bash "${BATS_TEST_DIRNAME}"/../install-bashhub.sh
}

@test "install_hooks_for_shell should install for bash" {
  SHELL=$(which bash)
  run 'install_hooks_for_shell'
  [[ $status == 0 ]]
  in_profile=$(grep -q 'bashhub.sh' ~/.bashrc; echo $?;)
  [[ "$in_profile" == 0 ]]
}

@test "install_hooks_for_shell should install for zsh" {
  SHELL=$(which zsh)
  run 'install_hooks_for_shell'
  [[ $status == 0 ]]
  in_profile=$(grep -q 'bashhub.zsh' ~/.zshrc; echo $?;)
  [[ "$in_profile" == 0 ]]
}

@test "install_hooks_for_shell should fail for unsupported" {
  unset SHELL
  run 'install_hooks_for_shell'
  [[ $status == 1 ]]
}

