driver.execute_script("""
/* ============================= */
/* HOODALGO OVERLAY v13          */
/* CLEAN ALIGNMENT BUILD         */
/* ============================= */

/* REMOVE EXISTING */
var old = document.getElementById('blackout_overlay');
if (old){
    old.remove();
}

/* LOAD FONT */
if (!document.getElementById('hoodalgo_font')){
    var font = document.createElement('link');
    font.id = 'hoodalgo_font';
    font.href = 'https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap';
    font.rel = 'stylesheet';
    document.head.appendChild(font);
}

/* ============================= */
/* OVERLAY                       */
/* ============================= */

var overlay = document.createElement('div');
overlay.id = 'blackout_overlay';

overlay.style.position = 'fixed';
overlay.style.top = '0';
overlay.style.left = '0';
overlay.style.width = '100vw';
overlay.style.height = '100vh';

overlay.style.background = 'rgba(0,0,0,0.62)';
overlay.style.backdropFilter = 'blur(10px)';
overlay.style.zIndex = '999999999';

overlay.style.display = 'flex';
overlay.style.alignItems = 'center';
overlay.style.justifyContent = 'center';

overlay.style.opacity = '0';
overlay.style.transition = 'opacity 0.4s ease';

/* ============================= */
/* STACK                         */
/* ============================= */

var stack = document.createElement('div');

stack.style.display = 'flex';
stack.style.flexDirection = 'column';
stack.style.alignItems = 'center';

stack.style.gap = '16px';

stack.style.transform = 'translateY(10px)';
stack.style.opacity = '0';
stack.style.transition = 'all 0.4s ease';

/* ============================= */
/* LOGO                          */
/* ============================= */

var logo = document.createElement('div');

logo.style.display = 'flex';
logo.style.alignItems = 'flex-end';

logo.style.fontFamily = 'Poppins, sans-serif';
logo.style.fontWeight = '800';

logo.style.fontSize = '72px';
logo.style.letterSpacing = '-2px';

/* Hood */
var hood = document.createElement('span');
hood.innerText = 'Hood';
hood.style.color = '#4ade80';

/* Algo */
var algo = document.createElement('span');
algo.style.display = 'flex';
algo.style.alignItems = 'center';
algo.style.marginLeft = '8px';

/* Alg text */
var alg_text = document.createElement('span');
alg_text.innerText = 'Alg';
alg_text.style.color = '#ffffff';

/* Gear */
var gear = document.createElement('span');
gear.innerText = '⚙️';

gear.style.display = 'inline-block';
gear.style.fontSize = '82px';

gear.style.marginLeft = '-5px';
gear.style.marginRight = '-6px';

gear.style.position = 'relative';
gear.style.top = '8px';

gear.style.animation = 'spin 4s linear infinite';

/* Build logo */
algo.appendChild(alg_text);
algo.appendChild(gear);

logo.appendChild(hood);
logo.appendChild(algo);

/* ============================= */
/* STATUS ROW (FIXED)            */
/* ============================= */

var status = document.createElement('div');

status.style.display = 'flex';
status.style.alignItems = 'center';
status.style.gap = '10px';
status.style.marginTop = '30px';

/* Dot */
var dot = document.createElement('div');

dot.style.width = '9px';
dot.style.height = '9px';

dot.style.borderRadius = '50%';
dot.style.background = '#4ade80';

dot.style.boxShadow = '0 0 10px rgba(74,222,128,1)';

dot.style.animation = 'pulse 1.4s ease-in-out infinite';
dot.style.position = 'relative';
dot.style.top = '1px';

/* Text */
var text = document.createElement('div');

text.innerText = 'Scanning portfolio';

text.style.color = 'white';
text.style.fontSize = '22px';
text.style.fontWeight = '500';

/* Animated dots */
var dots = document.createElement('span');
dots.style.marginLeft = '6px';

/* ============================= */
/* SUB NOTE                      */
/* ============================= */

var sub = document.createElement('div');

sub.innerText = 'Portfolio screen faded to protect privacy';

sub.style.fontSize = '13px';
sub.style.color = '#6b7280';

sub.style.marginTop = '6px';
sub.style.opacity = '0.8';

/* ============================= */
/* ANIMATIONS                    */
/* ============================= */

if (!document.getElementById('overlay_anim')){

    var style = document.createElement('style');
    style.id = 'overlay_anim';

    style.innerHTML = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes pulse {
        0% { opacity: 0.3; transform: scale(0.85); }
        50% { opacity: 1; transform: scale(1.2); }
        100% { opacity: 0.3; transform: scale(0.85); }
    }
    `;

    document.head.appendChild(style);
}

/* ============================= */
/* DOT LOOP                      */
/* ============================= */

var dot_count = 0;

setInterval(function(){
    dot_count = (dot_count + 1) % 4;
    dots.innerText = '.'.repeat(dot_count);
}, 500);

/* ============================= */
/* BUILD                         */
/* ============================= */

status.appendChild(dot);
status.appendChild(text);
status.appendChild(dots);

stack.appendChild(logo);
stack.appendChild(status);
stack.appendChild(sub);

overlay.appendChild(stack);
document.body.appendChild(overlay);

/* ============================= */
/* ENTRANCE                      */
/* ============================= */

setTimeout(function(){

    overlay.style.opacity = '1';
    stack.style.opacity = '1';
    stack.style.transform = 'translateY(0px)';

}, 10);

""")