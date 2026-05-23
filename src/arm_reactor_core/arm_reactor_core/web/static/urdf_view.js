/* urdf_view.js — three.js + urdf-loader 기반 OpenArm 양손 URDF 시각화.
 *
 * 1. /api/config fetch → mode === 'urdf' 일 때만 init
 * 2. /api/openarm/urdf fetch → URDFLoader.parse(xml) → robot Object3D
 * 3. mesh URL 변환: package://openarm_description/... → /api/meshes/openarm_description/...
 * 4. /ws/joint_states subscribe → robot.setJointValue(name, position) 매 message
 * 5. animate loop (requestAnimationFrame, OrbitControls + grid + lights)
 */
(function() {
    'use strict';

    let renderer = null, scene = null, camera = null, controls = null;
    let robot = null;

    async function init() {
        let cfg;
        try {
            cfg = await fetch('/api/config').then(r => r.json());
        } catch (e) {
            console.warn('[urdf_view] /api/config fetch failed', e);
            return;
        }
        if (cfg.arm_view_mode !== 'urdf') {
            console.log('[urdf_view] arm_view_mode != urdf, skip init');
            return;
        }
        if (!window.THREE) { console.error('[urdf_view] THREE not loaded'); return; }
        if (!window.URDFLoader) { console.error('[urdf_view] URDFLoader not loaded'); return; }

        const canvas = document.getElementById('urdf-canvas');
        if (!canvas) {
            console.error('[urdf_view] #urdf-canvas not found');
            return;
        }

        // ─── three.js scene ──────────────────────────────────
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x303030);

        const w = canvas.clientWidth || 480, h = canvas.clientHeight || 360;
        camera = new THREE.PerspectiveCamera(45, w / h, 0.01, 100);
        camera.position.set(1.5, 1.2, 1.5);
        camera.lookAt(0, 0.5, 0);

        renderer = new THREE.WebGLRenderer({canvas: canvas, antialias: true});
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(w, h, false);

        scene.add(new THREE.AmbientLight(0xffffff, 0.6));
        const dir = new THREE.DirectionalLight(0xffffff, 0.8);
        dir.position.set(2, 3, 2);
        scene.add(dir);

        scene.add(new THREE.GridHelper(2, 20, 0x666666, 0x444444));

        // OrbitControls — three r140 examples/js 의 UMD (THREE.OrbitControls)
        if (window.THREE.OrbitControls) {
            controls = new THREE.OrbitControls(camera, canvas);
            controls.target.set(0, 0.5, 0);
            controls.update();
        }

        // ─── URDF load ───────────────────────────────────────
        let xml;
        try {
            xml = await fetch('/api/openarm/urdf').then(r => {
                if (!r.ok) throw new Error(`urdf fetch ${r.status}`);
                return r.text();
            });
        } catch (e) {
            console.error('[urdf_view] urdf fetch failed', e);
            return;
        }

        // urdf-loader UMD: window.URDFLoader (class)
        const loader = new URDFLoader();
        // mesh URL resolver: 'package://<pkg>/...' → '/api/meshes/<pkg>/...'
        loader.packages = (pkg) => `/api/meshes/${pkg}`;
        loader.loadMeshCb = function(path, manager, done) {
            const ext = path.split('.').pop().toLowerCase();
            if (ext === 'stl' && window.THREE.STLLoader) {
                new THREE.STLLoader(manager).load(path, (geom) => {
                    const mat = new THREE.MeshPhongMaterial({color: 0x888888});
                    done(new THREE.Mesh(geom, mat));
                }, undefined, (err) => { console.warn('STL load fail', path, err); done(null); });
            } else if ((ext === 'dae' || ext === 'collada') && window.THREE.ColladaLoader) {
                new THREE.ColladaLoader(manager).load(path, (col) => done(col.scene),
                    undefined, (err) => { console.warn('DAE load fail', path, err); done(null); });
            } else {
                console.warn('[urdf_view] unsupported mesh:', path);
                done(null);
            }
        };

        robot = loader.parse(xml);
        // ROS z-up → three.js y-up 변환 (URDF 가 정자로 보이도록 -90° X 축 회전)
        robot.rotation.x = -Math.PI / 2;
        scene.add(robot);
        console.log('[urdf_view] robot loaded, joints:', Object.keys(robot.joints || {}));

        // ─── joint_state WebSocket ───────────────────────────
        const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${wsProto}//${location.host}/ws/joint_states`);
        ws.addEventListener('message', (ev) => {
            try {
                const js = JSON.parse(ev.data);
                if (!robot || !robot.joints) return;
                for (const [name, pos] of Object.entries(js.positions)) {
                    const j = robot.joints[name];
                    if (j && typeof j.setJointValue === 'function') {
                        j.setJointValue(pos);
                    }
                }
            } catch (e) {
                console.warn('[urdf_view] joint_state parse error', e);
            }
        });
        ws.addEventListener('close', () => console.log('[urdf_view] joint_states ws closed'));
        ws.addEventListener('error', (e) => console.warn('[urdf_view] ws error', e));

        // ─── animate ─────────────────────────────────────────
        function animate() {
            requestAnimationFrame(animate);
            if (controls) controls.update();
            renderer.render(scene, camera);
        }
        animate();

        // resize observer
        window.addEventListener('resize', () => {
            const w2 = canvas.clientWidth || 480, h2 = canvas.clientHeight || 360;
            renderer.setSize(w2, h2, false);
            camera.aspect = w2 / h2;
            camera.updateProjectionMatrix();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
