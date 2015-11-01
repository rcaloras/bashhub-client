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
  BASH_VERSION=1
  run 'install_hooks_for_shell'
  [[ $status == 0 ]]
  in_profile=$(grep -q 'bashhub.sh' ~/.bashrc; echo $?;)
  [[ "$in_profile" == 0 ]]
}

@test "install_hooks_for_shell should install for zsh" {
  ZSH_VERSION=1
  run 'install_hooks_for_shell'
  [[ $status == 0 ]]
  in_profile=$(grep -q 'bashhub.zsh' ~/.zshrc; echo $?;)
  [[ "$in_profile" == 0 ]]
}

@test "install_hooks_for_shell should fail for unsupported" {
  unset BASH_VERSION
  run 'install_hooks_for_shell'
  [[ $status == 1 ]]
}

@test "generate .bash_profile and .bashrc and link them" {
  rm ~/.bashrc
  rm ~/.zshrc
  run 'generate_bash_config_file'
  [[ $status == 0 ]]
  [[ -f ~/.bashrc  ]]
  [[ -f ~/.bash_profile ]]
  # Should source .bashrc in .bash_profile
  in_profile=$(grep -q 'source ~/.bashrc' ~/.bash_profile; echo $?;)
  [[ "$in_profile" == 0 ]]
}

