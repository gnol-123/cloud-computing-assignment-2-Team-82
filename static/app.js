/* ==============================================
   app.js — Soundwave Music App
   Cloud Computing Assignment 2

   Updated to use img_url returned directly from
   Flask routes (/songs, /subscriptions) instead
   of calling /image/<artist> separately.

   Your teammate updated appFlask.py so that:
   - /songs returns img_url in each song object
   - /subscriptions returns img_url in each song
   - img_url is the direct S3 URL
   ============================================== */


// PAGE NAVIGATION
function showPage(n) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + n).classList.add('active');
  document.querySelectorAll('.alert').forEach(a => a.classList.remove('show'));
}

function setGreeting() {
  const h = new Date().getHours();
  const g = h < 12 ? 'Good morning,' : h < 17 ? 'Good afternoon,' : 'Good evening,';
  const el = document.getElementById('greeting-text');
  if (el) el.textContent = g;
}


// LOGIN
async function doLogin() {
  const email = document.getElementById('login-email').value.trim();
  const pass  = document.getElementById('login-password').value;
  const err   = document.getElementById('login-error');
  const btn   = document.getElementById('btn-login');
  err.classList.remove('show');

  if (!email || !pass) {
    err.textContent = 'Please enter your email and password.';
    err.classList.add('show'); return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    err.textContent = 'Please enter a valid email address.';
    err.classList.add('show'); return;
  }

  btn.disabled = true; btn.textContent = 'Signing in…';
  try {
    const res  = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password: pass })
    });
    const data = await res.json();

    if (!res.ok || data.message === 'Incorrect password' || data.message === 'User not found') {
      err.textContent = 'email or password is invalid';
      err.classList.add('show'); return;
    }

    const uname = data.user_name || data.username;
    sessionStorage.setItem('sw_email', email);
    sessionStorage.setItem('sw_uname', uname);
    document.getElementById('login-email').value    = '';
    document.getElementById('login-password').value = '';
    await goMain(uname, email);

  } catch {
    err.textContent = 'Cannot reach server. Is Flask running?';
    err.classList.add('show');
  } finally {
    btn.disabled = false; btn.textContent = 'Sign In';
  }
}


// REGISTER
async function doRegister() {
  const email = document.getElementById('reg-email').value.trim();
  const uname = document.getElementById('reg-username').value.trim();
  const pass  = document.getElementById('reg-password').value;
  const err   = document.getElementById('register-error');
  const ok    = document.getElementById('register-success');
  const btn   = document.getElementById('btn-register');
  err.classList.remove('show'); ok.classList.remove('show');

  if (!email || !uname || !pass) {
    err.textContent = 'Please fill in all fields.'; err.classList.add('show'); return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    err.textContent = 'Please enter a valid email address.'; err.classList.add('show'); return;
  }
  if (pass.length < 6) {
    err.textContent = 'Password must be at least 6 characters.'; err.classList.add('show'); return;
  }
  if (uname.length < 2) {
    err.textContent = 'Username must be at least 2 characters.'; err.classList.add('show'); return;
  }

  btn.disabled = true; btn.textContent = 'Creating account…';
  try {
    const res  = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, user_name: uname, password: pass })
    });
    const data = await res.json();

    if (res.status === 409) {
      err.textContent = 'The email already exists'; err.classList.add('show'); return;
    }
    if (!res.ok) {
      err.textContent = data.message || 'Registration failed.'; err.classList.add('show'); return;
    }

    ok.classList.add('show');
    setTimeout(() => {
      document.getElementById('reg-email').value    = '';
      document.getElementById('reg-username').value = '';
      document.getElementById('reg-password').value = '';
      showPage('login');
    }, 1500);

  } catch {
    err.textContent = 'Cannot reach server. Is Flask running?'; err.classList.add('show');
  } finally {
    btn.disabled = false; btn.textContent = 'Create Account';
  }
}


// LOGOUT
async function doLogout() {
  try { await fetch('/logout', { method: 'POST' }); } catch (_) {}
  sessionStorage.removeItem('sw_email');
  sessionStorage.removeItem('sw_uname');
  closePlayer();
  resetMain();
  showPage('login');
}


// MAIN PAGE
async function goMain(uname, email) {
  setGreeting();
  document.getElementById('nav-avatar').textContent        = uname.slice(0, 2).toUpperCase();
  document.getElementById('user-display-name').textContent = uname;
  resetQuery();
  await loadSubs(email, uname);
  showPage('main');
}

function resetMain() {
  document.getElementById('sub-list').innerHTML    = '';
  document.getElementById('result-list').innerHTML = '';
  document.getElementById('sub-empty').style.display = 'block';
  document.getElementById('sub-count').textContent   = '0';
  resetQuery();
}

function resetQuery() {
  document.getElementById('result-list').innerHTML = '';
  document.getElementById('no-result').classList.remove('show');
  document.getElementById('query-err').classList.remove('show');
  ['q-title', 'q-year', 'q-artist', 'q-album'].forEach(id => {
    document.getElementById(id).value = '';
  });
}


// SUBSCRIPTIONS — LOAD
// GET /subscriptions returns array of { artist, title, img_url, ... }
// img_url is now the direct S3 URL from your teammate's updated Flask
async function loadSubs(email, uname) {
  const list  = document.getElementById('sub-list');
  const empty = document.getElementById('sub-empty');
  const badge = document.getElementById('sub-count');

  email = email || sessionStorage.getItem('sw_email');
  uname = uname || sessionStorage.getItem('sw_uname');
  list.innerHTML = '';

  try {
    const res  = await fetch(`/subscriptions?email=${encodeURIComponent(email)}&user_name=${encodeURIComponent(uname)}`);
    const data = await res.json();
    const subs = Array.isArray(data) ? data : [];

    badge.textContent = subs.length;

    if (subs.length === 0) { empty.style.display = 'block'; return; }
    empty.style.display = 'none';

    // Each sub has { artist, title }
    // Fetch full details (including img_url) from /songs
    for (let i = 0; i < subs.length; i++) {
      const songs = await getSongDetail(subs[i].artist, subs[i].title);
      const song  = songs.length > 0 ? songs[0] : {
        title:   subs[i].title,
        artist:  subs[i].artist,
        year:    '',
        album:   '',
        img_url: subs[i].img_url || ''   // use img_url from sub if available
      };
      list.appendChild(makeRow(song, 'remove', i + 1));
    }

  } catch (e) { console.error('loadSubs error:', e); }
}

// Fetch full song details including img_url
async function getSongDetail(artist, title) {
  try {
    const res  = await fetch(`/songs?artist=${encodeURIComponent(artist)}&title=${encodeURIComponent(title)}`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch { return []; }
}


// SUBSCRIBE
async function doSubscribe(artist, title) {
  const email = sessionStorage.getItem('sw_email');
  const uname = sessionStorage.getItem('sw_uname');
  const btn   = document.querySelector(`[data-a="sub"][data-ar="${CSS.escape(artist)}"][data-ti="${CSS.escape(title)}"]`);

  if (btn) { btn.disabled = true; btn.textContent = 'Adding…'; }

  try {
    const res = await fetch('/subscriptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, user_name: uname, artist, title })
    });
    if (!res.ok) { if (btn) { btn.disabled = false; btn.textContent = '+ Subscribe'; } return; }
    await loadSubs(email, uname);
    refreshSubBtns();
  } catch { if (btn) { btn.disabled = false; btn.textContent = '+ Subscribe'; } }
}


// REMOVE
async function doRemove(artist, title) {
  const email = sessionStorage.getItem('sw_email');
  const uname = sessionStorage.getItem('sw_uname');
  const row   = document.querySelector(`#sub-list [data-ra="${CSS.escape(artist)}"][data-rt="${CSS.escape(title)}"]`);
  if (row) row.style.opacity = '0.4';

  try {
    const res = await fetch('/subscriptions', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, user_name: uname, artist, title })
    });
    if (!res.ok) { if (row) row.style.opacity = '1'; return; }
    await loadSubs(email, uname);
    refreshSubBtns();
  } catch { if (row) row.style.opacity = '1'; }
}

function isSub(artist, title) {
  return !!document.querySelector(`#sub-list [data-ra="${CSS.escape(artist)}"][data-rt="${CSS.escape(title)}"]`);
}

function refreshSubBtns() {
  document.querySelectorAll('[data-a="sub"]').forEach(b => {
    const s = isSub(b.dataset.ar, b.dataset.ti);
    b.disabled    = s;
    b.textContent = s ? '✓ Subscribed' : '+ Subscribe';
  });
}


// QUERY
// GET /songs returns array of songs each with img_url already included
async function doQuery() {
  const title  = document.getElementById('q-title').value.trim();
  const year   = document.getElementById('q-year').value.trim();
  const artist = document.getElementById('q-artist').value.trim();
  const album  = document.getElementById('q-album').value.trim();

  const err  = document.getElementById('query-err');
  const noRes = document.getElementById('no-result');
  const list  = document.getElementById('result-list');
  const btn   = document.getElementById('btn-query');

  err.classList.remove('show'); noRes.classList.remove('show');
  list.innerHTML = '';

  if (!title && !year && !artist && !album) { err.classList.add('show'); return; }

  btn.disabled = true;
  btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2.5"/><path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg> Searching…';

  try {
    const p = new URLSearchParams();
    if (title)  p.append('title',  title);
    if (year)   p.append('year',   year);
    if (artist) p.append('artist', artist);
    if (album)  p.append('album',  album);

    const res   = await fetch('/songs?' + p.toString());
    const songs = await res.json();

    if (!Array.isArray(songs) || songs.length === 0) {
      noRes.classList.add('show'); return;
    }

    // songs array already contains img_url from your teammate's updated Flask
    songs.forEach((s, i) => list.appendChild(makeRow(s, 'subscribe', i + 1)));

  } catch {
    err.textContent = 'Cannot reach server. Is Flask running?';
    err.classList.add('show');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2.5"/><path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg> Search';
  }
}


// MUSIC PLAYER — DEEZER PREVIEW
async function playPreview(artist, title, imgUrl) {
  const bg      = document.getElementById('player-bg');
  const art     = document.getElementById('player-art');
  const audio   = document.getElementById('player-audio');
  const songEl  = document.getElementById('player-song');
  const artEl   = document.getElementById('player-artist-modal');
  const albEl   = document.getElementById('player-album-modal');
  const errEl   = document.getElementById('player-err');
  const modal   = document.getElementById('player-modal');
  const npBar   = document.getElementById('np-bar');
  const npBg    = document.getElementById('np-bg');
  const npArt   = document.getElementById('np-art');
  const npAudio = document.getElementById('np-audio');
  const npSong  = document.getElementById('np-song');
  const npABar  = document.getElementById('np-artist-bar');

  // Reset
  audio.src = ''; errEl.textContent = '';
  songEl.textContent = 'Loading…';
  artEl.textContent  = artist;
  albEl.textContent  = '';

  // Use img_url from song data as background immediately
  // This is now the direct S3 URL from your teammate's updated Flask
  if (imgUrl) {
    bg.style.backgroundImage   = `url('${imgUrl}')`;
    npBg.style.backgroundImage = `url('${imgUrl}')`;
    art.src   = imgUrl;
    npArt.src = imgUrl;
  } else {
    bg.style.backgroundImage   = 'none';
    npBg.style.backgroundImage = 'none';
  }

  modal.classList.add('open');

  try {
    // Call Flask /play which calls Deezer API for 30s preview
    const res  = await fetch(`/play?title=${encodeURIComponent(title)}&artist=${encodeURIComponent(artist)}`);
    const data = await res.json();

    if (!res.ok || data.error) {
      songEl.textContent = title;
      errEl.textContent  = '⚠ Preview not available for this song';
      return;
    }

    songEl.textContent = data.title  || title;
    artEl.textContent  = data.artist || artist;
    albEl.textContent  = data.album  || '';

    // If Deezer returns album cover, use it as background
    // Otherwise keep the S3 artist image
    if (data.cover) {
      bg.style.backgroundImage   = `url('${data.cover}')`;
      npBg.style.backgroundImage = `url('${data.cover}')`;
      art.src   = data.cover;
      npArt.src = data.cover;
    }

    // Play the 30s preview
    audio.src = data.preview_url;
    audio.load();
    audio.play().catch(() => { errEl.textContent = 'Click ▶ to start playback'; });

    // Update now playing bar
    npSong.textContent = data.title  || title;
    npABar.textContent = data.artist || artist;
    npAudio.src = data.preview_url;
    npBar.classList.add('on');

  } catch {
    songEl.textContent = title;
    errEl.textContent  = '⚠ Could not load preview.';
  }
}

function openModal()  { document.getElementById('player-modal').classList.add('open'); }
function closeModal() { document.getElementById('player-modal').classList.remove('open'); }
function openPlayer() { openModal(); }

function closePlayer() {
  const audio  = document.getElementById('player-audio');
  const npAudio = document.getElementById('np-audio');
  audio.pause();   audio.src   = '';
  npAudio.pause(); npAudio.src = '';
  document.getElementById('player-modal').classList.remove('open');
  document.getElementById('np-bar').classList.remove('on');
}

document.getElementById('player-modal')?.addEventListener('click', function (e) {
  if (e.target === this) closeModal();
});


// ROW BUILDER
// Now uses song.img_url directly (S3 URL from Flask)
// instead of building /image/<artist> path
function makeRow(song, action, num) {
  const row = document.createElement('div');
  row.className    = 'song-row';
  row.dataset.ra   = song.artist;
  row.dataset.rt   = song.title;

  // Use img_url from song data — direct S3 URL
  // Falls back to placeholder if not available
  const imgHTML = song.img_url
    ? `<img
         class="row-thumb"
         src="${esc(song.img_url)}"
         alt="${esc(song.artist)}"
         onerror="this.outerHTML='<div class=\\'row-ph\\'>♪</div>'"
       >`
    : `<div class="row-ph">♪</div>`;

  const sub = isSub(song.artist, song.title);

  const actionBtn = action === 'remove'
    ? `<button class="btn-rem" onclick="doRemove('${esc(song.artist)}','${esc(song.title)}')">Remove</button>`
    : `<button
         class="btn-sub"
         data-a="sub"
         data-ar="${esc(song.artist)}"
         data-ti="${esc(song.title)}"
         onclick="doSubscribe('${esc(song.artist)}','${esc(song.title)}')"
         ${sub ? 'disabled' : ''}>
         ${sub ? '✓ Subscribed' : '+ Subscribe'}
       </button>`;

  // Pass img_url to playPreview so it can use it as background
  const imgUrl = song.img_url || '';

  row.innerHTML = `
    ${imgHTML}
    <div class="row-info">
      <div class="row-title">${esc(song.title)}</div>
      <div class="row-meta">${esc(song.artist)}${song.album ? ' · ' + esc(song.album) : ''}</div>
    </div>
    <div class="row-year">${esc(song.year || '')}</div>
    <div class="row-actions">
      ${actionBtn}
      <button
        class="btn-play"
        onclick="playPreview('${esc(song.artist)}','${esc(song.title)}','${esc(imgUrl)}')">
        ▶
      </button>
    </div>
  `;
  return row;
}


// SECURITY — HTML escape
function esc(s) {
  if (typeof s !== 'string') s = String(s || '');
  return s
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}


// ENTER KEY
document.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  const a = document.querySelector('.page.active');
  if      (a.id === 'page-login')    doLogin();
  else if (a.id === 'page-register') doRegister();
  else if (a.id === 'page-main')     doQuery();
});


// SESSION RESTORE
(async function () {
  const u = sessionStorage.getItem('sw_uname');
  const e = sessionStorage.getItem('sw_email');
  if (u && e) await goMain(u, e);
})();