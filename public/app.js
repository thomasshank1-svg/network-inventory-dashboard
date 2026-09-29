let state = { devices: [], online: 0 };
function render() {
  $("#online").textContent = `${state.online}/${state.devices.length} online`;
  $("#devices").innerHTML = state.devices.map((device) => `
    <article class="item device">
      <div><span class="pill">${esc(device.kind)}</span><h3>${esc(device.hostname)}</h3><p class="mono">${esc(device.ip)}</p><p>${esc(device.owner)} · warranty ${esc(device.warranty_until)}</p></div>
      <div class="stack">
        <select data-status="${device.id}">${["Online", "Watch", "Offline"].map((s) => `<option ${s === device.status ? "selected" : ""}>${s}</option>`).join("")}</select>
        <textarea data-notes="${device.id}">${esc(device.notes)}</textarea>
        <button data-save="${device.id}">Save</button>
      </div>
    </article>
  `).join("");
  document.querySelectorAll("[data-save]").forEach((button) => button.addEventListener("click", () => action(button, async () => {
    await api("/api/status", { id: Number(button.dataset.save), status: document.querySelector(`[data-status="${button.dataset.save}"]`).value, notes: document.querySelector(`[data-notes="${button.dataset.save}"]`).value });
    await refresh();
  })));
}
async function refresh() { state = await api("/api/state"); render(); }
$("#deviceForm").addEventListener("submit", (event) => {
  event.preventDefault();
  action(event.submitter, async () => {
    await api("/api/devices", Object.fromEntries(new FormData(event.currentTarget)));
    event.currentTarget.reset();
    await refresh();
  });
});
refresh().catch((error) => toast(error.message));
