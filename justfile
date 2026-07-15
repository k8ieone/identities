app_id := "one.k8ie.Identities"
manifest := app_id + ".json"
command := "identities"

# 1. Build the app incrementally (NO --force-clean, NO --install)
build:
    flatpak-builder --force-clean --sandbox --user --install-deps-from=flathub --ccache --disable-tests flatpak-build {{manifest}}

# 2. Run directly from the build directory
run: build
    flatpak-builder --run --sandbox flatpak-build {{manifest}} {{command}}

