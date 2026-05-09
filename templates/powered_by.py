driver.execute_script("""

/* ============================= */
/* HOODALGO HUD v20 (LOGO FIX)   */
/* ============================= */

/* REMOVE EXISTING */
var old = document.getElementById('hoodalgo_hud');
if (old){ old.remove(); }

/* LOAD FONT */
if (!document.getElementById('hoodalgo_font')){
    var font = document.createElement('link');
    font.id = 'hoodalgo_font';
    font.href = 'https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap';
    font.rel = 'stylesheet';
    document.head.appendChild(font);
}

/* ============================= */
/* CONTAINER                     */
/* ============================= */

var hud = document.createElement('div');
hud.id = 'hoodalgo_hud';
hud.style.position = 'fixed';
hud.style.top = '16px';
hud.style.left = '16px';
hud.style.padding = '20px 26px';
hud.style.background = 'rgba(0,0,0,0.92)';
hud.style.borderRadius = '18px';
hud.style.zIndex = '999999999';
hud.style.fontFamily = 'Poppins, sans-serif';
hud.style.pointerEvents = 'none';
hud.style.opacity = '0';
hud.style.textAlign = 'center';

hud.style.boxShadow = "0 12px 50px rgba(0,0,0,0.85), 0 0 20px rgba(0,255,157,0.25), 0 0 60px rgba(0,255,157,0.18), 0 0 120px rgba(0,255,157,0.12)";

/* HEADER */
var title = document.createElement('div');
title.textContent = 'Automation powered by:';
title.style.color = '#9aa0a6';
title.style.fontSize = '13px';
title.style.marginBottom = '10px';

/* ROW */
var row = document.createElement('div');
row.style.display = 'flex';
row.style.alignItems = 'center';
row.style.justifyContent = 'center';

/* DOT */
var dot = document.createElement('span');
dot.style.width = '9px';
dot.style.height = '9px';
dot.style.background = '#00ff9d';
dot.style.borderRadius = '50%';
dot.style.marginRight = '10px';
dot.style.boxShadow = '0 0 16px rgba(0,255,157,1)';

/* TEXT */
var text = document.createElement('span');
text.style.display = 'flex';
text.style.alignItems = 'flex-end';
text.style.fontWeight = '800';
text.style.fontSize = '28px';
text.style.letterSpacing = '-0.5px';

/* Hood */
var hood = document.createElement('span');
hood.textContent = 'Hood';
hood.style.color = '#4ade80';

/* Algo container */
var algo = document.createElement('span');
algo.style.display = 'flex';
algo.style.alignItems = 'center';
algo.style.marginLeft = '0px';

/* Alg text */
var alg_text = document.createElement('span');
alg_text.textContent = 'Alg';
alg_text.style.color = '#ffffff';

/* SPINNING EMOJI GEAR */
var gear = document.createElement('span');
gear.textContent = '⚙️';
gear.style.display = 'inline-block';
gear.style.marginLeft = '0px';
gear.style.marginRight = '0px';
gear.style.position = 'relative';
gear.style.top = '2px';
gear.style.animation = 'hoodalgo_spin 3.8s linear infinite';

/* ============================= */
/* ANIMATIONS                    */
/* ============================= */

if (!document.getElementById('hoodalgo_anim')){
    var style = document.createElement('style');
    style.id = 'hoodalgo_anim';

    style.textContent = `
    @keyframes hoodalgo_fade_in {
        0% { opacity: 0; transform: translate3d(0,-12px,0); }
        100% { opacity: 1; transform: translate3d(0,0,0); }
    }
    @keyframes hoodalgo_pulse {
        0% { opacity: 0.4; transform: scale(0.85); }
        50% { opacity: 1; transform: scale(1.25); }
        100% { opacity: 0.4; transform: scale(0.85); }
    }
    @keyframes hoodalgo_spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    `;

    document.head.appendChild(style);
}

/* APPLY */
hud.style.animation = 'hoodalgo_fade_in 0.4s ease forwards';
dot.style.animation = 'hoodalgo_pulse 1.3s infinite';

/* BUILD */
algo.appendChild(alg_text);
algo.appendChild(gear);

text.appendChild(hood);
text.appendChild(algo);

row.appendChild(dot);
row.appendChild(text);

hud.appendChild(title);
hud.appendChild(row);

document.body.appendChild(hud);

""")