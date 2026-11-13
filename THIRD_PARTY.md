# Third-party components

- **mtkclient**, B. Kerler and contributors: https://github.com/bkerler/mtkclient . GPL-3.0; pinned base `118a000a83ea31c4f427fe5225abfe964546e05e`. `patches/mtkclient-118a000.patch` modifies its device-ID configuration and read/file-writer completion handling. The patch is included as source. The optional setup script obtains mtkclient from its own repository; local device metadata and binaries are not included in this package.
- **PyUSB**: https://github.com/pyusb/pyusb . Installed as a dependency; retain its upstream license when redistributing it.
- **Python / Tkinter**: external runtime. Native system fonts are used. No Naver font files are included.
- **Android Platform-Tools**: external Google tools. Not bundled or relicensed here.
- **MisterZtr LineageOS GSI**: https://github.com/MisterZtr/LineageOS_gsi . Referenced as a tested external image. No image is bundled, and no official Npay device support is claimed.

The project source and included mtkclient patch are offered under GPL-3.0. Third-party firmware, fonts, APKs and driver packages keep their respective ownership and licensing; this repository does not grant rights to redistribute those assets.
