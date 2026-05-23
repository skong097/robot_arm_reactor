# vendor — three.js + urdf-loader (UMD, browser)

dashboard 의 urdf_view.js 가 사용하는 browser 라이브러리 vendored static 모음.
build step 없이 직접 `<script src="/static/vendor/...js">` 로 로드.

## 부트스트랩 (한 번)

```bash
cd src/arm_reactor_core/arm_reactor_core/web/static/vendor

wget -O three.min.js https://unpkg.com/three@0.140.0/build/three.min.js
wget -O STLLoader.js https://unpkg.com/three@0.140.0/examples/js/loaders/STLLoader.js
wget -O ColladaLoader.js https://unpkg.com/three@0.140.0/examples/js/loaders/ColladaLoader.js
wget -O OrbitControls.js https://unpkg.com/three@0.140.0/examples/js/controls/OrbitControls.js
wget -O URDFLoader.js https://unpkg.com/urdf-loader@0.10.4/umd/URDFLoader.js
```

## Versions
- three.js: **r140** (UMD build) — r150+ 에서 `examples/js` 가 제거되어 ESM 만 남음. urdf-loader 0.10.4 가 r140 과 호환되는 UMD examples 의존.
- urdf-loader: 0.10.4 (UMD)
- OrbitControls: r140 examples/js (urdf_view.js 가 사용 — 마우스 drag scene rotate)

## License
- three.js: MIT
- urdf-loader: Apache-2.0

## .gitignore
이 디렉토리의 `.js` 파일은 .gitignore 의 어떤 룰에도 안 매치 (현 .gitignore 의 *.tflite/*.task/*.onnx 외). git 추적 정상.
