# Sequence Cartography

Mapping moving images: Sequence Cartography turns a video into a navigable map of its scenes.

For every detected scene it renders an **OM image**, a composite overview made of three bands:

1. **Keyframes**: one large frame roughly every 5 seconds
2. **Thumbnails**: five small frames per keyframe
3. **Slit-scan stripe**: the centre pixel column of every frame, laid out over time

Sources can be local video files or online videos.

## Status

The project is being restarted. The original 2018/19 prototype (Python + OpenCV + PySceneDetect) is kept for reference in [`legacy/`](legacy/).

## License

TBD
