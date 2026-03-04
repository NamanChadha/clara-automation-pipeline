/**
 * Clara Automation Pipeline - Dashboard App
 * Loads pipeline outputs from local JSON files and displays
 * account data, agent specs, and version diffs.
 */

// ============================================================================
// DATA LOADING
// ============================================================================

// Account data will be loaded from the outputs directory
// In a real deployment, this would use a backend API
// For local viewing, we embed the data directly

let accountsData = {};
let currentAccount = null;
let currentAgentVersion = 'v2';

/**
 * Initialize the dashboard.
 * Attempts to load data from embedded JSON or fetches from outputs/.
 */
async function init() {
    // Try to load account data
    try {
        await loadAccountsFromFetch();
    } catch (e) {
        console.warn('Could not fetch data, using embedded data:', e.message);
        loadEmbeddedData();
    }

    populateAccountSelector();
    setupTabs();
    showOverview();
}

/**
 * Load account data by fetching JSON files from the outputs directory.
 */
async function loadAccountsFromFetch() {
    // List of known account IDs (could be dynamic with a manifest file)
    const accountIds = [
        'bens_electric_solutions',
        'prestige_fire_protection',
        'comfort_zone_hvac',
        'guardian_alarm_systems',
        'allstar_plumbing_mechanical',
    ];

    for (const id of accountIds) {
        try {
            const v1Memo = await fetchJSON(`../outputs/accounts/${id}/v1/account_memo.json`);
            const v2Memo = await fetchJSON(`../outputs/accounts/${id}/v2/account_memo.json`);
            const v1Spec = await fetchJSON(`../outputs/accounts/${id}/v1/agent_spec.json`);
            const v2Spec = await fetchJSON(`../outputs/accounts/${id}/v2/agent_spec.json`);
            const changes = await fetchJSON(`../outputs/accounts/${id}/changes.json`);
            const changelog = await fetchText(`../outputs/accounts/${id}/changelog.md`);

            accountsData[id] = {
                id,
                company_name: v1Memo?.company_name || id,
                v1: { memo: v1Memo, spec: v1Spec },
                v2: { memo: v2Memo, spec: v2Spec },
                changes: changes,
                changelog: changelog,
            };
        } catch (e) {
            console.warn(`Could not load data for ${id}:`, e.message);
        }
    }
}

async function fetchJSON(url) {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
}

async function fetchText(url) {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.text();
}

/**
 * Fallback: load embedded sample data for demo purposes
 */
function loadEmbeddedData() {
    accountsData = {
        'bens_electric_solutions': {
            id: 'bens_electric_solutions',
            company_name: "Ben's Electric Solutions",
            v1: { memo: { note: 'Load from outputs/accounts/bens_electric_solutions/v1/' }, spec: {} },
            v2: { memo: { note: 'Load from outputs/accounts/bens_electric_solutions/v2/' }, spec: {} },
            changes: { total_changes: 0, changes: [] },
            changelog: '# No data loaded\nPlease serve this directory with a local HTTP server.',
        }
    };
}

// ============================================================================
// UI SETUP
// ============================================================================

function populateAccountSelector() {
    const select = document.getElementById('account-select');
    select.innerHTML = '<option value="">-- Choose an account --</option>';

    for (const [id, data] of Object.entries(accountsData)) {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = `${data.company_name} (${id})`;
        select.appendChild(opt);
    }

    select.addEventListener('change', (e) => {
        currentAccount = accountsData[e.target.value] || null;
        if (currentAccount) {
            renderCurrentTab();
        }
    });
}

function setupTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const tabName = tab.dataset.tab;
            showPanel(tabName);
        });
    });
}

function showPanel(name) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById(`panel-${name}`);
    if (panel) {
        panel.classList.add('active');
        renderPanel(name);
    }
}

function renderCurrentTab() {
    const activeTab = document.querySelector('.tab.active');
    if (activeTab) {
        renderPanel(activeTab.dataset.tab);
    }
}

function renderPanel(name) {
    if (!currentAccount && name !== 'overview') return;

    switch (name) {
        case 'overview': showOverview(); break;
        case 'v1': showVersion('v1'); break;
        case 'v2': showVersion('v2'); break;
        case 'diff': showDiff(); break;
        case 'changelog': showChangelog(); break;
        case 'agent': showAgentSpec(); break;
    }
}

// ============================================================================
// RENDERING
// ============================================================================

function showOverview() {
    const grid = document.getElementById('stats-grid');
    const totalAccounts = Object.keys(accountsData).length;
    let totalChanges = 0;
    let accountsWithV2 = 0;

    for (const data of Object.values(accountsData)) {
        if (data.changes?.total_changes) totalChanges += data.changes.total_changes;
        if (data.v2?.memo) accountsWithV2++;
    }

    grid.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${totalAccounts}</div>
            <div class="stat-label">Total Accounts</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${totalAccounts}</div>
            <div class="stat-label">v1 Generated</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${accountsWithV2}</div>
            <div class="stat-label">v2 Updated</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${totalChanges}</div>
            <div class="stat-label">Total Changes</div>
        </div>
    `;
}

function showVersion(version) {
    if (!currentAccount) return;
    const el = document.getElementById(`${version}-content`);
    const data = currentAccount[version]?.memo;
    el.textContent = data ? syntaxHighlight(JSON.stringify(data, null, 2)) : 'No data available';
    el.innerHTML = data ? syntaxHighlight(JSON.stringify(data, null, 2)) : '<span style="color:var(--text-muted)">No data available</span>';
}

function showDiff() {
    if (!currentAccount) return;
    const container = document.getElementById('diff-content');
    const countEl = document.getElementById('diff-count');
    const changes = currentAccount.changes?.changes || [];

    countEl.textContent = `${changes.length} change(s)`;

    if (changes.length === 0) {
        container.innerHTML = '<p style="color:var(--text-muted); text-align:center; padding:40px;">No changes detected between v1 and v2.</p>';
        return;
    }

    let html = '';
    for (const change of changes) {
        const oldVal = typeof change.old_value === 'object'
            ? JSON.stringify(change.old_value, null, 2)
            : String(change.old_value || '(not set)');
        const newVal = typeof change.new_value === 'object'
            ? JSON.stringify(change.new_value, null, 2)
            : String(change.new_value || '(not set)');

        html += `
            <div class="diff-field">
                <div class="diff-field-header">
                    <span class="field-name">${escapeHtml(change.field)}</span>
                    <span class="reason">${escapeHtml(change.reason || '')}</span>
                </div>
                <div class="diff-row">
                    <div class="diff-side old">
                        <span class="diff-side-label">v1 (Demo)</span>
                        ${escapeHtml(oldVal)}
                    </div>
                    <div class="diff-side new">
                        <span class="diff-side-label">v2 (Onboarding)</span>
                        ${escapeHtml(newVal)}
                    </div>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

function showChangelog() {
    if (!currentAccount) return;
    const el = document.getElementById('changelog-content');
    const md = currentAccount.changelog || 'No changelog available.';
    el.innerHTML = renderMarkdown(md);
}

function showAgentSpec() {
    if (!currentAccount) return;
    const el = document.getElementById('agent-content');
    const spec = currentAccount[currentAgentVersion]?.spec;
    el.innerHTML = spec ? syntaxHighlight(JSON.stringify(spec, null, 2)) : '<span style="color:var(--text-muted)">No agent spec available</span>';
}

window.showAgentVersion = function(version) {
    currentAgentVersion = version;
    document.getElementById('agent-v1-btn').classList.toggle('active', version === 'v1');
    document.getElementById('agent-v2-btn').classList.toggle('active', version === 'v2');
    showAgentSpec();
};

// ============================================================================
// UTILITIES
// ============================================================================

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function syntaxHighlight(json) {
    json = escapeHtml(json);
    return json.replace(
        /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
        function (match) {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            const colors = {
                key: 'var(--accent)',
                string: 'var(--green)',
                number: 'var(--yellow)',
                boolean: 'var(--purple)',
                null: 'var(--red)',
            };
            return `<span style="color:${colors[cls]}">${match}</span>`;
        }
    );
}

function renderMarkdown(md) {
    // Simple markdown renderer for changelog display
    let html = md
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/^---$/gm, '<hr>')
        .replace(/```json\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/```\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/<li>/g, '<ul><li>').replace(/<\/li>\n(?!<li>)/g, '</li></ul>');
    return html;
}

// ============================================================================
// INIT
// ============================================================================

document.addEventListener('DOMContentLoaded', init);
