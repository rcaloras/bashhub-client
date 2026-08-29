#!/usr/bin/env bats

setup() {
    release_script="$BATS_TEST_DIRNAME/../../script/release"
}

make_release_repo() {
    release_repo="$BATS_TEST_TMPDIR/release-repo"
    release_origin="$BATS_TEST_TMPDIR/release-origin.git"
    fake_bin="$BATS_TEST_TMPDIR/bin"

    mkdir -p "$release_repo/script" "$release_repo/bashhub" "$fake_bin"
    cp "$release_script" "$release_repo/script/release"
    printf '%s\n' '[project]' 'name = "bashhub"' > "$release_repo/pyproject.toml"

    git init -q "$release_repo"
    git -C "$release_repo" symbolic-ref HEAD refs/heads/master
    git -C "$release_repo" config user.name 'Release Test'
    git -C "$release_repo" config user.email 'release-test@example.com'
    git -C "$release_repo" add pyproject.toml script/release
    git -C "$release_repo" commit -qm 'Initial commit'
    git -C "$release_repo" tag 3.1.0

    git init -q --bare "$release_origin"
    git -C "$release_repo" remote add origin "$release_origin"
    git -C "$release_repo" push -qu origin master --tags
    git -C "$release_origin" symbolic-ref HEAD refs/heads/master
    git -C "$release_repo" remote set-head origin --auto >/dev/null

    printf '%s\n' \
        '#!/bin/sh' \
        'if [ "$1" = release ] && [ "$2" = view ]; then exit 1; fi' \
        'if [ "$1" = release ] && [ "$2" = list ]; then printf "%s\\n" "Blue Beagle"; exit 0; fi' \
        'exit 2' > "$fake_bin/gh"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$fake_bin/uv"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$fake_bin/bats"
    chmod +x "$fake_bin/gh" "$fake_bin/uv" "$fake_bin/bats"
}

@test "release script has valid Bash syntax" {
    run bash -n "$release_script"

    [ "$status" -eq 0 ]
}

@test "release script documents its command-line interface" {
    run "$release_script" --help

    [ "$status" -eq 0 ]
    [[ "$output" == *'Usage: script/release'* ]]
    [[ "$output" == *'Color Dog'* ]]
    [[ "$output" == *'--dry-run'* ]]
}

@test "release script rejects an invalid version" {
    run "$release_script" not-a-version

    [ "$status" -eq 1 ]
    [[ "$output" == *'version must be a PEP 440 release'* ]]
}

@test "release dry run validates a unique title without changing the repository" {
    make_release_repo
    cd "$release_repo"

    run env PATH="$fake_bin:$PATH" script/release --dry-run 3.2.0 "Teal Corgi"

    [ "$status" -eq 0 ]
    [[ "$output" == *'Version: 3.1.0 -> 3.2.0'* ]]
    [[ "$output" == *'Title:   Teal Corgi'* ]]
    [[ "$output" == *'Dry run complete'* ]]
    ! git rev-parse --quiet --verify refs/tags/3.2.0
    [ -z "$(git status --porcelain)" ]
}

@test "release script rejects a title already used by a GitHub release" {
    make_release_repo
    cd "$release_repo"

    run env PATH="$fake_bin:$PATH" script/release --dry-run 3.2.0 "Blue Beagle"

    [ "$status" -eq 1 ]
    [[ "$output" == *'release title is already in use: Blue Beagle'* ]]
}

@test "release dry run generates an unused Color Dog title" {
    make_release_repo
    cd "$release_repo"

    run env PATH="$fake_bin:$PATH" script/release --dry-run 3.2.0

    [ "$status" -eq 0 ]
    [[ "$output" =~ Title:[[:space:]]+[[:alpha:]]+[[:space:]][[:alpha:]]+ ]]
    [[ "$output" != *'Title:   Blue Beagle'* ]]
}
