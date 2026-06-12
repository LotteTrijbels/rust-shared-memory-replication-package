import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = "repos" # Local clone directory used for analysis (not part of replication package)
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "..", "primitive_counts_results.json")

ANALYSED_FILES = [
    "rustdesk/rustdesk/src/client.rs",
    "rustdesk/rustdesk/src/rendezvous_mediator.rs",
    "rustdesk/rustdesk/src/server.rs",
    "rustdesk/rustdesk/src/client/io_loop.rs",

    "dani-garcia/vaultwarden/src/config.rs",
    "dani-garcia/vaultwarden/src/http_client.rs",
    "dani-garcia/vaultwarden/src/main.rs",
    "dani-garcia/vaultwarden/src/api/icons.rs",
    "dani-garcia/vaultwarden/src/db/mod.rs",

    "topjohnwu/Magisk/native/src/core/daemon.rs",
    "topjohnwu/Magisk/native/src/core/logging.rs",
    "topjohnwu/Magisk/native/src/core/thread.rs",
    "topjohnwu/Magisk/native/src/core/su/daemon.rs",

    "alacritty/alacritty/alacritty/src/logging.rs",
    "alacritty/alacritty/alacritty/src/renderer/mod.rs",
    "alacritty/alacritty/alacritty_terminal/src/event_loop.rs",
    "alacritty/alacritty/alacritty_terminal/src/sync.rs",
    "alacritty/alacritty/alacritty_terminal/src/tty/windows/child.rs",

    "helix-editor/helix/helix-dap/src/transport.rs",
    "helix-editor/helix/helix-event/src/redraw.rs",
    "helix-editor/helix/helix-event/src/registry.rs",
    "helix-editor/helix/helix-event/src/runtime.rs",
    "helix-editor/helix/helix-term/src/application.rs",
    "helix-editor/helix/helix-view/src/document.rs",
    
    "farion1231/cc-switch/src-tauri/src/lib.rs",
    "farion1231/cc-switch/src-tauri/src/commands/webdav_auto_sync.rs",
    "farion1231/cc-switch/src-tauri/src/proxy/circuit_breaker.rs",
    "farion1231/cc-switch/src-tauri/src/proxy/response_processor.rs",
    "farion1231/cc-switch/src-tauri/src/proxy/server.rs",
    "farion1231/cc-switch/src-tauri/src/services/webdav_auto_sync.rs",

    "sharkdp/fd/src/main.rs",
    "sharkdp/fd/src/walk.rs",

    "nushell/nushell/crates/nu-protocol/src/pipeline/handlers.rs",
    "nushell/nushell/crates/nu-utils/src/sync/keyed_lazy_lock.rs",
    "nushell/nushell/crates/nu-plugin-core/src/interface/stream/mod.rs",
    "nushell/nushell/crates/nu-protocol/src/engine/engine_state.rs",
    "nushell/nushell/crates/nu-command/src/network/http/client.rs",

    "lapce/lapce/lapce-app/src/editor_tab.rs",
    "lapce/lapce/lapce-app/src/plugin.rs",
    "lapce/lapce/lapce-proxy/src/dispatch.rs",
    "lapce/lapce/lapce-proxy/src/plugin/lsp.rs",
    "lapce/lapce/lapce-rpc/src/core.rs",

    "sxyazi/yazi/yazi-core/src/tasks/tasks.rs",
    "sxyazi/yazi/yazi-dds/src/server.rs",
    "sxyazi/yazi/yazi-dds/src/pubsub.rs",
    "sxyazi/yazi/yazi-runner/src/loader/loader.rs",
    "sxyazi/yazi/yazi-scheduler/src/scheduler.rs",
    "sxyazi/yazi/yazi-scheduler/src/worker.rs",
    
    "casey/just/src/analyzer.rs",
    "casey/just/src/dependency.rs",
    "casey/just/src/justfile.rs",
    "casey/just/src/ran.rs",
    "casey/just/src/signal_handler.rs",

    "firecracker/src/firecracker/src/api_server_adapter.rs",
    "firecracker/src/firecracker/src/main.rs",
    "firecracker/src/vmm/src/builder.rs",
    "firecracker/src/vmm/src/lib.rs",
    "firecracker/src/vmm/src/vstate/vcpu.rs",
    "firecracker/src/vmm/src/vstate/vm.rs",
]
ANALYSED_SET = set(ANALYSED_FILES)

PRIMITIVES = {
    "Arc": re.compile(r"\bArc\b"),
    "Weak": re.compile(r"\bWeak\b"),
    "Mutex": re.compile(r"\bMutex\b"),
    "RwLock": re.compile(r"\bRwLock\b"),
    "FairMutex": re.compile(r"\bFairMutex\b"),
    "Atomic": re.compile(r"\bAtomic[A-Z]\w*"),
    "AtomicArc": re.compile(r"\bAtomicArc\b"),
    "OnceLock": re.compile(r"\bOnceLock\b"),
    "LazyLock": re.compile(r"\bLazyLock\b"),
    "Condvar": re.compile(r"\bCondvar\b"),
    "Barrier": re.compile(r"\bBarrier\b"),
    "Semaphore": re.compile(r"\bSemaphore\b"),
    "ArcSwap": re.compile(r"\bArcSwap\b"),
    "RuntimeLocal": re.compile(r"\bRuntimeLocal\b"),
    "RwSignal": re.compile(r"\bRwSignal\b"),
}

EXCLUDE_DIRS = {
    "tests",
    "test",
    "benches",
    "bench",
    "examples",
    "example",
    "target",
}

def should_skip(path_parts: list[str]) -> bool:
    return any(part in EXCLUDE_DIRS for part in path_parts)

def clean_code(content: str) -> str:
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL) # block comments

    lines = []
    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("//"): # line comment
            continue

        if stripped.startswith("use "): # imports
            continue

        lines.append(line)

    return "\n".join(lines)

def count_primitives_in_file(filepath: str):
    counts = {k: 0 for k in PRIMITIVES}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        content = clean_code(content)

        for name, pattern in PRIMITIVES.items():
            counts[name] += len(pattern.findall(content))

    except Exception:
        pass

    return counts

def main():
    results = []

    for rel_path in ANALYSED_FILES:
        full_path = os.path.join(BASE_DIR, rel_path)

        if not os.path.exists(full_path):
            continue

        counts = count_primitives_in_file(full_path)

        results.append({
            "file": rel_path,
            "counts": counts,
            "binary": {
                k: int(v > 0)
                for k, v in counts.items()
            }
        })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()