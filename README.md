# Identities

A modern frontend for [`pass`](https://www.passwordstore.org/) built for GNOME.

## Features

 - Adaptive UI - works great on phones and small screens
 - Supports as many arbitrary attributes as you want
 - Generates TOTPs (even multiple per file)
 - Support for adding multiple password stores in arbitrary locations

![Desktop screenshot](misc/screenshots/password.png)

## Download

You can get Identities both natively and as a Flatpak.

### Flatpak

<a href='https://flathub.org/en/apps/one.k8ie.Identities'>
    <img width='240' alt='Get it on Flathub' src='https://flathub.org/api/badge?locale=en'/>
</a>

Release builds are available on [Flathub](https://flathub.org/en/apps/one.k8ie.Identities)!

Install using `flatpak install one.k8ie.Identities`.

Brave souls can get the latest preview build as an artifact from [GitHub Actions](https://github.com/k8ieone/identities/actions/workflows/flatpak.yml).

Note: GPG in Flatpak can be buggy - see [#32](https://github.com/k8ieone/identities/issues/32). If you run into issues with GPG freezig or not being available, please open an issue. I'd also recommend you try the native builds listed below.

### Arch Linux

Available on the AUR! Install using you favorite [AUR helper](https://wiki.archlinux.org/title/AUR_helpers) or [install manually](https://wiki.archlinux.org/title/Arch_User_Repository#Installing_and_upgrading_packages).

- [Stable package](https://aur.archlinux.org/packages/identities)
- [Development package](https://aur.archlinux.org/packages/identities-git)

### Alpine / postmarketOS

Available in Alpine Edge ([testing](https://pkgs.alpinelinux.org/packages?name=identities&branch=edge&repo=&arch=&origin=&flagged=&maintainer=) repository).

If you're on a stable release of Alpine or postmarketOS and don't want to switch to `edge` just to use Identities, you can follow [these instructions](https://wiki.alpinelinux.org/wiki/Repositories#Using_testing_repository) to add the `testing` repo on a stable release.

After you're done, you can simply install Identities like so:

```
apk add identities@testing
```

### Your distro!

Maintaining packages can be a challenge, so I truly appreciate any help! If you'd like to package Identities for your distribution, I'd love to have you involved.  
Feel free to open an issue / PR if you'd like to have your package listed here!

## Roadmap

See [issues](https://github.com/k8ieone/identities/issues) for more currently planned features.
