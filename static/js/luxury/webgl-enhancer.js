import { SELECTORS, WEBGL } from "./config.js";

export class WebGLEnhancer {
  constructor({ reducedMotion }) {
    this.reducedMotion = reducedMotion;
    this.canvas = null;
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.textureLoader = null;
    this.mediaPlanes = [];
    this.heroObject = null;
    this.rafId = null;
    this.viewportWidth = window.innerWidth;
    this.viewportHeight = window.innerHeight;
  }

  init() {
    if (this.reducedMotion || !window.THREE || this.viewportWidth < 960) {
      document.body.classList.add("webgl-disabled");
      return;
    }

    this.canvas = document.querySelector(SELECTORS.webglCanvas);
    if (!this.canvas) {
      return;
    }

    const mediaElements = Array.from(document.querySelectorAll(SELECTORS.webglMedia))
      .filter((element) => element.tagName === "IMG" && (element.currentSrc || element.src))
      .slice(0, WEBGL.maxMediaPlanes);

    if (!mediaElements.length) {
      document.body.classList.add("webgl-disabled");
      return;
    }

    this.setupThreeContext();
    this.createMediaPlanes(mediaElements);
    this.createHeroObject();
    this.attachEvents();
    this.animate();
  }

  setupThreeContext() {
    const THREE = window.THREE;

    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    this.renderer.setSize(this.viewportWidth, this.viewportHeight);
    this.renderer.setClearColor(0x000000, 0);

    this.scene = new THREE.Scene();
    this.camera = new THREE.OrthographicCamera(0, this.viewportWidth, this.viewportHeight, 0, -1000, 1000);
    this.camera.position.z = 10;

    this.textureLoader = new THREE.TextureLoader();
  }

  createMediaPlanes(mediaElements) {
    const THREE = window.THREE;
    const geometry = new THREE.PlaneGeometry(1, 1, 16, 16);

    mediaElements.forEach((element) => {
      const textureSrc = element.currentSrc || element.src;
      if (!textureSrc) {
        return;
      }

      const texture = this.textureLoader.load(textureSrc);
      texture.colorSpace = THREE.SRGBColorSpace;

      const uniforms = {
        uTexture: { value: texture },
        uTime: { value: 0 },
        uHover: { value: 0 },
        uScroll: { value: 0 },
      };

      const material = new THREE.ShaderMaterial({
        uniforms,
        transparent: true,
        depthWrite: false,
        vertexShader: `
          varying vec2 vUv;
          uniform float uTime;
          uniform float uHover;
          uniform float uScroll;

          void main() {
            vUv = uv;
            vec3 transformed = position;
            float wave = sin((uv.y + uTime * 0.25) * 10.0) * 1.6 * uHover;
            float scrollWave = cos((uv.x + uScroll * 0.0012) * 8.0) * 1.2;
            transformed.z += wave + scrollWave;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(transformed, 1.0);
          }
        `,
        fragmentShader: `
          varying vec2 vUv;
          uniform sampler2D uTexture;
          uniform float uHover;
          uniform float uTime;

          void main() {
            vec2 uv = vUv;
            uv.x += sin((uv.y * 12.0) + (uTime * 1.1)) * ${WEBGL.waveAmplitude.toFixed(4)} * uHover;
            uv.y += cos((uv.x * 12.0) + (uTime * 0.9)) * ${WEBGL.waveAmplitude.toFixed(4)} * uHover;
            vec4 tex = texture2D(uTexture, uv);
            float alpha = (${WEBGL.baseOpacity.toFixed(2)} + (${(WEBGL.maxHoverOpacity - WEBGL.baseOpacity).toFixed(2)} * uHover)) * tex.a;
            gl_FragColor = vec4(tex.rgb, alpha);
          }
        `,
      });

      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.z = 4;
      this.scene.add(mesh);

      const planeData = {
        element,
        mesh,
        uniforms,
        hover: 0,
        hoverTarget: 0,
      };

      element.addEventListener("mouseenter", () => {
        planeData.hoverTarget = 1;
      });
      element.addEventListener("mouseleave", () => {
        planeData.hoverTarget = 0;
      });
      element.addEventListener("focus", () => {
        planeData.hoverTarget = 1;
      });
      element.addEventListener("blur", () => {
        planeData.hoverTarget = 0;
      });

      this.mediaPlanes.push(planeData);
    });
  }

  createHeroObject() {
    const THREE = window.THREE;
    const hero = document.querySelector(SELECTORS.hero);
    if (!hero || this.viewportWidth < 1024) {
      return;
    }

    const geometry = new THREE.TorusKnotGeometry(52, 10, 160, 24);
    const material = new THREE.MeshBasicMaterial({
      color: 0xb3001b,
      wireframe: true,
      transparent: true,
      opacity: 0.24,
    });
    this.heroObject = new THREE.Mesh(geometry, material);
    this.heroObject.position.set(this.viewportWidth * 0.83, this.viewportHeight * 0.72, 28);
    this.scene.add(this.heroObject);
  }

  attachEvents() {
    window.addEventListener("resize", this.onResize, { passive: true });
  }

  onResize = () => {
    this.viewportWidth = window.innerWidth;
    this.viewportHeight = window.innerHeight;

    if (!this.renderer || !this.camera) {
      return;
    }

    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    this.renderer.setSize(this.viewportWidth, this.viewportHeight);
    this.camera.left = 0;
    this.camera.right = this.viewportWidth;
    this.camera.top = this.viewportHeight;
    this.camera.bottom = 0;
    this.camera.updateProjectionMatrix();

    if (this.heroObject && this.viewportWidth >= 1024) {
      this.heroObject.position.set(this.viewportWidth * 0.83, this.viewportHeight * 0.72, 28);
    }
  };

  syncPlaneToElement(planeData) {
    const rect = planeData.element.getBoundingClientRect();
    const inView = rect.bottom > -80 && rect.top < this.viewportHeight + 80 && rect.right > -80 && rect.left < this.viewportWidth + 80;
    planeData.mesh.visible = inView;
    if (!inView) {
      return;
    }

    const centerX = rect.left + rect.width / 2;
    const centerY = this.viewportHeight - (rect.top + rect.height / 2);
    planeData.mesh.position.x = centerX;
    planeData.mesh.position.y = centerY;
    planeData.mesh.scale.x = Math.max(1, rect.width);
    planeData.mesh.scale.y = Math.max(1, rect.height);
  }

  animate = () => {
    if (!this.renderer || !this.scene || !this.camera) {
      return;
    }

    const now = performance.now() * 0.001;
    const scrollY = window.scrollY;

    this.mediaPlanes.forEach((planeData) => {
      this.syncPlaneToElement(planeData);
      planeData.hover += (planeData.hoverTarget - planeData.hover) * 0.12;
      planeData.uniforms.uHover.value = planeData.hover;
      planeData.uniforms.uTime.value = now;
      planeData.uniforms.uScroll.value = scrollY;
    });

    if (this.heroObject) {
      this.heroObject.rotation.x = 0.7 + Math.sin(now * 0.3) * 0.1;
      this.heroObject.rotation.y = now * 0.28 + scrollY * 0.0003;
      this.heroObject.rotation.z = Math.cos(now * 0.2) * 0.08;
    }

    this.renderer.render(this.scene, this.camera);
    this.rafId = window.requestAnimationFrame(this.animate);
  };
}
