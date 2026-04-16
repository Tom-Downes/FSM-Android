"""
p4a build hook — patches Lottie presplash template to disable looping.

p4a's default lottie.xml uses lottie_loop="true" which loops the entire
animation. We want lottie_loop="false" so the intro plays once and the
spinner (which runs to frame 36000) plays until the app loads.
"""
import glob
import os


def _patch_lottie():
    search_roots = [
        os.path.expanduser("~/.buildozer"),
        "/usr/local/lib",
        "/usr/lib",
        "/opt",
    ]
    patched = 0
    for root in search_roots:
        for path in glob.glob(os.path.join(root, "**", "lottie.xml"), recursive=True):
            if "bootstrap" not in path and "template" not in path:
                continue
            try:
                with open(path) as f:
                    content = f.read()
                if 'lottie_loop="true"' in content:
                    content = content.replace('lottie_loop="true"', 'lottie_loop="false"')
                    with open(path, "w") as f:
                        f.write(content)
                    print(f"[p4a_hook] Patched lottie_loop -> false: {path}")
                    patched += 1
            except Exception as e:
                print(f"[p4a_hook] Could not patch {path}: {e}")
    if patched == 0:
        print("[p4a_hook] WARNING: no lottie.xml bootstrap template found to patch")


def pre_build(buildozer):
    _patch_lottie()


def before_apk_build(buildozer):
    _patch_lottie()


def before_aab_build(buildozer):
    _patch_lottie()
