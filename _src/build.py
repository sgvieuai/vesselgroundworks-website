"""Build the Vessel Groundworks site.

Outputs:
  site/      production files (full HTML documents, pretty URLs, absolute canonical)
  preview/   artifact preview (main page as a fragment, other pages as full docs, .html links)
"""
import json, os, re, shutil, sys
from html import escape, unescape
from PIL import Image

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
# In the GitHub repo the site lives at the repo root (next to CNAME); in the scratch workspace it's in site/.
REPO_MODE = os.path.exists(os.path.join(ROOT, "CNAME"))
SITE = ROOT if REPO_MODE else os.path.join(ROOT, "site")
PREVIEW = os.path.join(ROOT, "preview")
DOMAIN = "https://vesselgroundworks.com"
LASTMOD = "2026-10-16"  # sitemap date; bump when page content changes

REPAIR_RATE = 95  # sprinkler repair labor, $/hour, plus parts, 1-hour minimum
PHONE_DISPLAY = "(385) 398-9355"
PHONE_TEL = "+13853989355"
EMAIL = "sergio@vesselgroundworks.com"
GOOGLE_REVIEWS = "https://www.google.com/maps?cid=12567048390870205497"
FACEBOOK = "https://www.facebook.com/profile.php?id=61595151076525"
INSTAGRAM = "https://www.instagram.com/vesselgroundworks"
TOWNS = ["Springville", "Mapleton", "Spanish Fork", "Salem", "Payson", "Provo", "Orem"]

CSS = open(os.path.join(SRC, "styles.css")).read()
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500'
         '&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=Saira+Condensed:wght@600;700;800&display=swap">')

# ---------- icons ----------
I_PHONE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>'
I_TEXT = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4 3h16a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 1-2zm3 6v2h10V9zm0 4v2h7v-2z"/></svg>'
I_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg>'

# ---------- images ----------
_dims = {}
def dims(name):
    if name not in _dims:
        _dims[name] = Image.open(os.path.join(SITE, "images", name + ".webp")).size
        _dims[name + "-sm"] = Image.open(os.path.join(SITE, "images", name + "-sm.webp")).size
    return _dims[name], _dims[name + "-sm"]

def img(name, alt, sizes="(max-width: 760px) 100vw, 50vw", eager=False):
    (w, h), (sw, _) = dims(name)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img src="images/{name}.webp" srcset="images/{name}-sm.webp {sw}w, images/{name}.webp {w}w" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{escape(alt)}" {load}>')

# ---------- reviews ----------
REVIEWS = {
    "brandon": ("Sergio and his crew were awesome! They did great work, communicated well throughout the whole process, were honest and trustworthy. I would recommend them to anyone and will use them again in the future. We hired them to do a whole remodel of our landscaping including installing sprinklers, cement curbing, sod and xeriscaping. It turned out great, we are very pleased with the quality and care that went into their work.", "Brandon H.", "Full landscape remodel"),
    "mason": ("Sergio was awesome! I have had him come out and do several different things for me with my sprinklers and each time he has been timely, does a great job, and does it for a fair price. Will definitely have him be my go to sprinkler guy for anything I need.", "Mason B.", "Sprinkler repairs"),
    "joshua": ("Sergio did a great job explaining what was going on with our system and explaining different options to fix it within our budget! We came up with a plan and he was diligent and honest with his work. Everything looks and works fantastic! A+", "Joshua J.", "Sprinkler system"),
    "kasha": ("Sergio was great! He responded very quick via text, and had our sprinklers fixed within 15mins of him being here. I would highly recommend them to anyone looking for help!", "Kasha Z.", "Sprinkler repair"),
    "aaron": ("Sergio helped me with a few landscape retaining walls in my backyard, they turned out great!", "Aaron K.", "Retaining walls"),
    "bryce": ("My new Sprinkler Guy. Great job", "Bryce M.", "Sprinkler repair"),
}

def quotes(keys):
    out = []
    for k in keys:
        text, who, job = REVIEWS[k]
        out.append(f'<figure class="quote"><div class="stars" aria-label="5 out of 5 stars">★★★★★</div>'
                   f'<blockquote><p>{escape(text)}</p></blockquote>'
                   f'<figcaption>{who} · {job} · Google review</figcaption></figure>')
    return "".join(out)

def reviews_section(keys, heading="What customers say"):
    return f'''
<section class="section section-alt" id="reviews" aria-labelledby="reviews-h">
  <div class="wrap">
    <div class="reviews-top">
      <div class="section-head" style="margin-bottom:0">
        <p class="label">Google reviews</p>
        <h2 id="reviews-h">{heading}</h2>
      </div>
      <div class="score"><b>5.0</b><div><div class="stars" aria-hidden="true">★★★★★</div><a class="textlink" href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener">Read all 20 reviews on Google</a></div></div>
    </div>
    <div class="quotes">{quotes(keys)}</div>
  </div>
</section>'''

# ---------- shared blocks ----------
def proof():
    items = [
        '<span class="stars" aria-hidden="true">★★★★★</span> 5.0 · 20 Google reviews',
        I_CHECK + "Free estimates",
        I_CHECK + "Same-day response",
        I_CHECK + "Hablamos español",
    ]
    return '<ul class="proof">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def cta_buttons(text_label="Call or text " + PHONE_DISPLAY, second=None):
    second_html = second or f'<a class="btn btn-line" href="sms:{PHONE_TEL}">{I_TEXT}Text a photo</a>'
    return (f'<div class="cta-row"><a class="btn btn-orange" href="tel:{PHONE_TEL}">{I_PHONE}{text_label}</a>{second_html}</div>')

def area_section():
    rows = [f'<li>{t}{"<span>Home base</span>" if t == "Springville" else ""}</li>' for t in TOWNS]
    rows.append('<li>Wasatch Front<span>Larger projects</span></li>')
    return f'''
<section class="section" id="area" aria-labelledby="area-h">
  <div class="wrap area">
    <div class="section-head">
      <p class="label">Service area</p>
      <h2 id="area-h">Based in Springville, working across Utah County</h2>
      <p class="lede">Sprinkler repairs mostly stay close to home. Bigger landscape and excavation projects can go anywhere along the Wasatch Front. Not sure if you're in range? Send a text and ask.</p>
    </div>
    <ul class="towns">{"".join(rows)}</ul>
  </div>
</section>'''

def rebate_section(compact=False, calc_href=None):
    head = "Upgrading? Check the water rebates first" if compact else "Utah may pay you to replace your lawn"
    body = ("Central Utah Water's Landscape Incentive Program pays part of the cost when you switch spray-watered flower beds to drip. Smart controllers have their own rebate. The full lawn-replacement rebate is on our xeriscaping page."
            if compact else
            "Utah County homeowners can get paid to replace lawn with water-wise landscaping through Central Utah Water's Landscape Incentive Program. The rate depends on your town.")
    body2 = "" if compact else ("<p>Two rules matter most. The program has to visit and approve the project before any grass comes out, and half the new area has to be planted, so a rock-only yard won't qualify. "
                                "In towns with secondary water, those site visits pause from October 15 to April 15. Winter is the time to plan: we'll measure, photograph and draw the plan you need, so you can apply first thing in spring.</p>")
    rows = ([("Switch flower beds from spray to drip", "per sq ft", "$1.00", "$0.50"),
             ("Smart sprinkler controller", "up to, per controller", "$100", "$100")]
            if compact else
            [("Replace lawn with water-wise landscaping", "per sq ft", "$3.00", "$1.50"),
             ("Switch flower beds from spray to drip", "per sq ft", "$1.00", "$0.50"),
             ("Plant a tree with your project", "per tree, up to 10", "$50", "$50"),
             ("Smart sprinkler controller", "up to, per controller", "$100", "$100")])
    rate_rows = "".join(f'<div class="rate"><span class="what">{w}<span class="unit">{u}</span></span><span class="amt">{a}</span><span class="amt">{b}</span></div>' for w, u, a, b in rows)
    return f'''
<section class="section section-dark on-dark" aria-labelledby="rebate-h">
  <div class="wrap rebate">
    <div class="rebate-copy">
      <p class="label">Water-wise rebates</p>
      <h2 id="rebate-h">{head}</h2>
      <p class="lede">{body}</p>
      {body2}
      <div class="cta-row">{f'<a class="btn btn-orange" href="{calc_href}">Estimate your rebate</a>' if calc_href else ""}<a class="btn btn-line" href="https://www.utahwatersavers.com/program-eligibility-page" target="_blank" rel="noopener">Check your city on Utah Water Savers</a></div>
    </div>
    <div>
      <div class="rates" role="table" aria-label="Rebate amounts by town">
        <div class="rate rate-head" role="row"><span></span><span>Spanish Fork · Salem · Payson</span><span>Springville · Mapleton · Provo · Orem</span></div>
        {rate_rows}
      </div>
      <p class="fine" style="margin-top:12px">Residential rates from the Utah Water Savers program pages, October 2026. Rates and rules can change. Artificial turf, concrete and pavers don't qualify. The rebate is paid to the homeowner.</p>
    </div>
  </div>
</section>'''

def steps_section():
    steps = [
        ("Call or text", "Tell us what's going on. A photo or short video of the problem helps us bring the right parts."),
        ("Free estimate", "We look at the system or the yard and give you a clear price before any work starts."),
        ("We do the work", "Careful, clean work, from a single sprinkler head to a full yard."),
        ("Walkthrough", "We run the system or walk the finished yard with you, so you know everything works."),
    ]
    items = "".join(f'<li class="step"><span class="n">Step {i}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(steps, 1))
    return f'''
<section class="section" aria-labelledby="steps-h">
  <div class="wrap">
    <div class="section-head"><p class="label">How it works</p><h2 id="steps-h">From first text to finished job</h2></div>
    <ol class="steps" style="padding:0;margin:0">{items}</ol>
  </div>
</section>'''

def _plain(html_text):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", html_text))).strip()

def faq_section(qas):
    items = "".join(f"<details><summary>{escape(q)}</summary><p>{a}</p></details>" for q, a in qas)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _plain(a)}} for q, a in qas]}
    return f'''
<section class="section section-alt" id="faq" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="section-head"><p class="label">Questions</p><h2 id="faq-h">Common questions</h2></div>
    <div class="faq">{items}</div>
  </div>
  <script type="application/ld+json">{json.dumps(ld, separators=(",", ":"))}</script>
</section>'''

def cta_band(h="Got a sprinkler problem or a yard to redo?", sub="Call or text Sergio for a free estimate. Monday to Saturday, 8am to 6pm."):
    return f'''
<section class="cta-band on-dark" aria-labelledby="cta-h">
  <div class="wrap cta-inner">
    <div><h2 id="cta-h">{h}</h2><p class="lede">{sub}</p></div>
    {cta_buttons()}
  </div>
</section>'''

def gallery(items, cols_sizes="(max-width: 760px) 50vw, 33vw"):
    figs = "".join(f"<figure>{img(n, alt, cols_sizes)}<figcaption>{escape(cap)}</figcaption></figure>" for n, alt, cap in items)
    return f'<div class="gallery">{figs}</div>'

def fixes(items):
    return '<div class="fixes">' + "".join(f'<div class="fix"><h3>{t}</h3><p>{d}</p></div>' for t, d in items) + "</div>"

# ---------- rebate calculator ----------
TIER_A = ["Spanish Fork", "Salem", "Payson"]            # $3.00 lawn / $1.00 drip
TIER_B = ["Springville", "Mapleton", "Provo", "Orem"]   # $1.50 lawn / $0.50 drip
COST_LOW, COST_HIGH = 5, 15                             # typical Utah xeriscape $/sq ft

CALC_JS = """
(function(){
  var form=document.getElementById('calc-form'); if(!form) return;
  var RATES={a:{lawn:3,beds:1},b:{lawn:1.5,beds:0.5}};
  var LOW=%d, HIGH=%d, PHONE='%s';
  function num(id,max){var v=parseFloat(document.getElementById(id).value);if(!isFinite(v)||v<0)v=0;if(max!==undefined)v=Math.min(v,max);return v;}
  function usd(v){return '$'+Math.round(v).toLocaleString('en-US');}
  function rate(v){return '$'+v.toFixed(2);}
  function run(){
    var sel=document.getElementById('c-town'), opt=sel.options[sel.selectedIndex];
    var tier=opt.getAttribute('data-tier'), town=opt.value;
    var lawn=Math.round(num('c-lawn')), beds=Math.round(num('c-beds')), trees=Math.floor(num('c-trees',10));
    var ctrl=document.getElementById('c-ctrl').checked;
    var rows=[], total=0, note='';
    if(tier==='x'){
      document.getElementById('c-total').textContent='Check your city';
      note='Other cities run their own programs with their own rates. Use the Utah Water Savers link above, or text us your town and we will look it up.';
    }else{
      var r=RATES[tier];
      function add(label,amt){if(amt>0){rows.push([label,amt]);total+=amt;}}
      add('Lawn replacement: '+lawn.toLocaleString('en-US')+' sq ft \\u00d7 '+rate(r.lawn),lawn*r.lawn);
      add('Beds to drip: '+beds.toLocaleString('en-US')+' sq ft \\u00d7 '+rate(r.beds),beds*r.beds);
      add('Trees: '+trees+' \\u00d7 $50',trees*50);
      add('Smart controller (up to)',ctrl?100:0);
      document.getElementById('c-total').textContent=usd(total);
      note=lawn>0?('Typical Utah cost to xeriscape '+lawn.toLocaleString('en-US')+' sq ft: '+usd(lawn*LOW)+' to '+usd(lawn*HIGH)+' before the rebate. We give you an exact price after a free look.'):'Enter your lawn size to see the rebate and a typical price range.';
    }
    var box=document.getElementById('c-lines'); box.innerHTML='';
    rows.forEach(function(x){var d=document.createElement('div');var s=document.createElement('span');s.textContent=x[0];var b=document.createElement('b');b.textContent=usd(x[1]);d.appendChild(s);d.appendChild(b);box.appendChild(d);});
    box.hidden=rows.length===0;
    document.getElementById('c-note').textContent=note;
    var msg='Hi Sergio, I\\u2019m in '+(tier==='x'?'(my town)':town)+(lawn>0?(' with about '+lawn.toLocaleString('en-US')+' sq ft of lawn I\\u2019d like to replace.'):'.')+(total>0?(' The rebate calculator says about '+usd(total)+'.'):'')+' Can you take a look?';
    document.getElementById('c-text').href='sms:'+PHONE+'?&body='+encodeURIComponent(msg);
  }
  form.addEventListener('input',run); form.addEventListener('change',run); run();
})();
""" % (COST_LOW, COST_HIGH, PHONE_TEL)

def calculator_section(alt=False):
    opts = "".join(f'<option value="{t}" data-tier="b">{t}</option>' for t in TIER_B)
    opts += "".join(f'<option value="{t}" data-tier="a">{t}</option>' for t in TIER_A)
    opts += '<option value="other" data-tier="x">Another city</option>'
    return f'''
<section class="section{" section-alt" if alt else ""}" id="rebate-calculator" aria-labelledby="calc-h">
  <div class="wrap">
    <div class="section-head">
      <p class="label">Rebate calculator</p>
      <h2 id="calc-h">Estimate your water-wise rebate</h2>
      <p class="lede">Pick your town and enter roughly how much lawn you'd replace. It uses Central Utah Water's residential rates. The program confirms the real amount when it visits.</p>
    </div>
    <div class="calc">
      <form class="calc-form" id="calc-form" action="#" onsubmit="return false">
        <div class="field"><label for="c-town">Your town</label><select id="c-town">{opts}</select></div>
        <div class="field"><label for="c-lawn">Lawn to replace (sq ft)</label>
          <input id="c-lawn" type="number" inputmode="numeric" min="0" step="10" placeholder="e.g. 1000">
          <span class="hint">Not sure? Multiply length by width in feet. A 25 × 40 ft lawn is 1,000 sq ft.</span></div>
        <div class="field"><label for="c-beds">Flower beds switching from spray to drip (sq ft)</label>
          <input id="c-beds" type="number" inputmode="numeric" min="0" step="10" placeholder="Optional"></div>
        <div class="field"><label for="c-trees">New trees planted (up to 10)</label>
          <input id="c-trees" type="number" inputmode="numeric" min="0" max="10" step="1" placeholder="Optional"></div>
        <label class="check"><input id="c-ctrl" type="checkbox"> Adding a smart sprinkler controller</label>
      </form>
      <div class="calc-out on-dark" aria-live="polite">
        <p class="label">Estimated rebate</p>
        <p class="calc-total" id="c-total">$0</p>
        <div class="calc-lines" id="c-lines" hidden></div>
        <p class="calc-note" id="c-note">Enter your lawn size to see the rebate and a typical price range.</p>
        <p class="calc-note">The program has to approve the project before any grass comes out, and half the new area has to be planted. The rebate is paid to the homeowner after the finished yard passes inspection.</p>
        <div class="cta-row"><a class="btn btn-orange" id="c-text" href="sms:{PHONE_TEL}">{I_TEXT}Text this to Sergio</a></div>
      </div>
    </div>
  </div>
  <script>{CALC_JS}</script>
</section>'''

# ---------- schema ----------
BUSINESS = {
    "@context": "https://schema.org",
    "@type": "HomeAndConstructionBusiness",
    "@id": DOMAIN + "/#business",
    "name": "Vessel Groundworks",
    "url": DOMAIN + "/",
    "logo": DOMAIN + "/images/vessel-groundworks-logo-transparent.png",
    "image": DOMAIN + "/images/og-vessel-groundworks.jpg",
    "telephone": "+1-385-398-9355",
    "email": EMAIL,
    "description": "Landscaping, sprinkler repair, xeriscaping and excavation in Springville and across Utah County.",
    "address": {"@type": "PostalAddress", "addressLocality": "Springville", "addressRegion": "UT", "postalCode": "84663", "addressCountry": "US"},
    "areaServed": [{"@type": "City", "name": f"{t}, UT"} for t in TOWNS] + [{"@type": "AdministrativeArea", "name": "Utah County, UT"}],
    "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "08:00", "closes": "18:00"}],
    "knowsLanguage": ["en", "es"],
    "foundingDate": "2021-05-02",
    "sameAs": [GOOGLE_REVIEWS, FACEBOOK],  # add INSTAGRAM once that account exists
    "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Services", "itemListElement": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Sprinkler repair", "url": DOMAIN + "/sprinkler-repair-in-utah-county"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Sprinkler blowout and winterization", "url": DOMAIN + "/sprinkler-blowout-in-utah-county"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Xeriscaping and low-water landscaping", "url": DOMAIN + "/xeriscaping-in-utah-county"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Excavation, grading and site prep", "url": DOMAIN + "/excavation-in-utah-county"}},
    ]},
}

def service_schema(name, slug, desc):
    return {
        "@context": "https://schema.org", "@type": "Service", "name": name, "serviceType": name,
        "url": f"{DOMAIN}/{slug}", "description": desc,
        "provider": {"@id": DOMAIN + "/#business"},
        "areaServed": [{"@type": "City", "name": f"{t}, UT"} for t in TOWNS],
    }

def breadcrumb(name, slug):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": f"{DOMAIN}/{slug}"}]}

# ---------- page frame ----------
NAV = [("sprinkler-repair-in-utah-county", "Sprinkler repair"), ("sprinkler-blowout-in-utah-county", "Blowouts"), ("xeriscaping-in-utah-county", "Xeriscaping"), ("excavation-in-utah-county", "Excavation")]

def season_strip(link):
    return (f'<div class="season"><div class="wrap season-row"><p><b>Fall blowouts are open.</b> Springville shuts off pressurized irrigation around October 15. '
            f'Get your lines cleared before the first hard freeze.</p><a class="textlink" href="{link("sprinkler-blowout-in-utah-county")}">Book a blowout</a></div></div>')

def header(current, link):
    navlinks = "".join(f'<a href="{link(s)}"{" aria-current=\"page\"" if s == current else ""}>{t}</a>' for s, t in NAV)
    navlinks += f'<a href="{link("")}#reviews">Reviews</a>'
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-head on-dark">
  <div class="wrap head-row">
    <a class="brand" href="{link("")}" aria-label="Vessel Groundworks home"><img src="images/logo-white-480.png" width="480" height="145" alt="Vessel Groundworks"></a>
    <nav class="nav" aria-label="Main">{navlinks}</nav>
    <a class="btn btn-orange head-call" href="tel:{PHONE_TEL}">{I_PHONE}{PHONE_DISPLAY}</a>
    <details class="menu"><summary>Menu</summary><nav class="menu-panel" aria-label="Mobile">{navlinks}<a href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a></nav></details>
  </div>
</header>'''

def footer(link):
    svc = "".join(f'<li><a href="{link(s)}">{t}</a></li>' for s, t in NAV)
    svc += f'<li><a href="{link(COST_SLUG)}">Xeriscaping costs</a></li><li><a href="{link(STRIP_SLUG)}">Park strips</a></li>'
    towns = "".join(f"<li>{t}</li>" for t in TOWNS)
    return f'''
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand"><img src="images/logo-white-480.png" width="480" height="145" alt="Vessel Groundworks" loading="lazy"><p>Landscaping, sprinkler repair, xeriscaping and excavation in Springville and across Utah County.</p></div>
      <div><h4>Contact</h4><ul><li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li>Mon–Sat, 8am–6pm</li><li>Se habla español</li><li><a href="{escape(FACEBOOK)}" target="_blank" rel="noopener">Facebook</a></li></ul></div>
      <div><h4>Services</h4><ul>{svc}<li><a href="{GOOGLE_REVIEWS}" target="_blank" rel="noopener">Google reviews</a></li></ul></div>
      <div><h4>Areas</h4><ul>{towns}</ul></div>
    </div>
    <div class="foot-legal"><span>© 2026 Vessel Groundworks · Springville, Utah</span></div>
  </div>
</footer>
<div class="callbar"><a class="btn btn-orange" href="tel:{PHONE_TEL}">{I_PHONE}Call</a><a class="btn btn-line" style="border-color:var(--on-dark);color:var(--on-dark)" href="sms:{PHONE_TEL}">{I_TEXT}Text</a></div>'''

def head_tags(p):
    url = DOMAIN + ("/" if p["slug"] == "" else "/" + p["slug"])
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, separators=(",", ":"))}</script>' for s in p["schema"])
    return (f'<title>{escape(p["title"])}</title>'
            f'<meta name="description" content="{escape(p["desc"])}">'
            f'<link rel="canonical" href="{url}">'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="Vessel Groundworks">'
            f'<meta property="og:title" content="{escape(p["title"])}"><meta property="og:description" content="{escape(p["desc"])}">'
            f'<meta property="og:url" content="{url}"><meta property="og:image" content="{DOMAIN}/images/og-vessel-groundworks.jpg">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<meta name="theme-color" content="#1f2023">'
            f'<link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png"><link rel="apple-touch-icon" href="apple-touch-icon.png">'
            + ld)

def full_doc(p, body):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            + head_tags(p) + FONTS + f"<style>{CSS}</style></head><body>" + body + "</body></html>\n")

# ---------- pages ----------
def page_home(link):
    services = [
        ("sprinkler-repair-in-utah-county", "Sprinkler repair &amp; irrigation", "sprinkler-valve-manifold-install", "New sprinkler valve manifold with three valves before burial",
         "Broken heads, leaking valves, line breaks, low pressure and dry spots. We find what's wrong, fix it, and make sure every zone covers the way it should.",
         ["Heads &amp; rotors", "Valves &amp; manifolds", "Line breaks", "Pressure &amp; coverage", "Drip conversion"]),
        ("xeriscaping-in-utah-county", "Xeriscaping &amp; low-water landscaping", "xeriscape-side-yard-sod-rock-border", "Side yard with a small lawn framed by rock and drought-tolerant grasses",
         "Rock, drought-tolerant plants, drip irrigation and as much lawn as you want to keep. Lower water bills and less mowing, and the yard still looks finished.",
         ["Rock &amp; gravel", "Sod &amp; lawn reduction", "Park strips", "Drip irrigation", "Concrete curbing", "Planting"]),
        ("excavation-in-utah-county", "Excavation, grading &amp; site prep", "excavation-from-excavator-cab", "View from an excavator cab digging a deep residential excavation",
         "The work under the finished project: grading, trenching, and prep for concrete, drainage and retaining walls, done with compact equipment that fits residential yards.",
         ["Grading", "Trenching", "Concrete prep", "Drainage", "Retaining wall prep"]),
    ]
    rows = "".join(f'''
      <article class="svc">
        <a href="{link(s)}" tabindex="-1" aria-hidden="true">{img(im, alt, "(max-width: 760px) 100vw, 40vw")}</a>
        <div class="svc-body">
          <h3><a href="{link(s)}">{t}</a></h3>
          <p>{d}</p>
          <ul class="spec">{"".join(f"<li>{x}</li>" for x in spec)}</ul>
          <p><a class="textlink" href="{link(s)}">More about {t.split(" &amp;")[0].split(",")[0].lower()}</a></p>
        </div>
      </article>''' for s, t, im, alt, d, spec in services)

    ba = f'''
      <div class="ba">
        <div class="ba-pair">
          <figure>{img("xeriscape-rock-yard-before", "Front yard stripped to bare dirt before a xeriscape install", "(max-width: 760px) 50vw, 25vw")}<span class="tag">Before</span></figure>
          <figure>{img("xeriscape-rock-yard-after", "Same front yard finished with rock landscaping around a mature tree", "(max-width: 760px) 50vw, 25vw")}<span class="tag after">After</span></figure>
        </div>
        <h3>Lawn to rock xeriscape</h3>
        <p>Turf and old soil out, grade set, rock in around the existing tree.</p>
      </div>
      <div class="ba">
        <div class="ba-pair">
          <figure>{img("concrete-prep-excavation", "Compact track loader digging out a side yard for a driveway extension", "(max-width: 760px) 50vw, 25vw")}<span class="tag">Before</span></figure>
          <figure>{img("finished-concrete-driveway-extension", "Finished concrete driveway extension along a fence line", "(max-width: 760px) 50vw, 25vw")}<span class="tag after">After</span></figure>
        </div>
        <h3>Driveway extension</h3>
        <p>Dug out, base compacted, and ready for a clean concrete finish.</p>
      </div>'''

    gal = gallery([
        ("concrete-pad-pour-crew", "Crew finishing a new concrete pad with mountains behind", "Concrete pad, Utah County"),
        ("drip-irrigation-planting-bed", "Mulched planting bed with drip irrigation along a stone wall", "Drip-irrigated planting bed"),
        ("boulder-wall-skid-steer", "Skid steer setting boulders for a rock wall", "Boulder wall install"),
        ("lawn-with-rock-border-xeriscape", "Front lawn with concrete curbing and rock borders", "Lawn with rock borders"),
        ("sprinkler-valve-box-repair", "Rebuilt sprinkler valve manifold inside a valve box", "Valve box rebuild"),
        ("excavator-trenching", "Excavator digging a trench at a new home site", "Trenching"),
    ])

    faq = faq_section([
        ("What services does Vessel Groundworks offer?", "Sprinkler repair and irrigation, xeriscaping and low-water landscaping, and excavation work like grading, trenching, drainage, concrete prep and retaining wall prep."),
        ("Do you take small jobs as well as big projects?", "Yes. We handle everything from a single broken sprinkler head to full landscape installs and multi-phase excavation projects."),
        ("What areas do you serve?", "We're based in Springville and work across Utah County, including Mapleton, Spanish Fork, Salem, Payson, Provo and Orem. Larger projects can go anywhere along the Wasatch Front. Outside that? Text us and ask."),
        ("Do you specialize in water-efficient landscaping?", "Yes. Rock work, drought-tolerant planting, drip irrigation, grading and edging are a big part of what we do, and we can explain how Utah's lawn-replacement rebate works."),
        ("Can you do the groundwork before landscaping or concrete?", "Yes. We do the excavation, grading, trenching, drainage and prep so the finished landscape or concrete starts on a solid, level base."),
        ("Are estimates free?", "Yes. Call or text and we'll set up a time to look at the job. You get a clear price before any work starts."),
    ])

    return f'''
<main id="main">
{season_strip(link)}
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="label">Springville, Utah · Serving Utah County</p>
      <h1>Landscaping &amp; sprinkler repair <span class="hl">in Utah County</span></h1>
      <p class="lede">From a broken sprinkler head to a full low-water yard, Vessel Groundworks handles the repair, the dirt work and the finished landscape. Call or text Sergio directly for a free estimate.</p>
      {cta_buttons(second=f'<a class="btn btn-line" href="sms:{PHONE_TEL}">{I_TEXT}Text a photo of your yard</a>')}
      {proof()}
    </div>
    <figure class="hero-photo" style="margin:0">
      {img("sod-and-rock-front-yard-utah-county", "Front yard with new sod, rock borders and ornamental grasses below the Wasatch mountains", "(max-width: 860px) 100vw, 46vw", eager=True)}
      <figcaption>Sod &amp; rock border install · Utah County</figcaption>
    </figure>
  </div>
</section>

<section class="section section-alt" id="services" aria-labelledby="svc-h">
  <div class="wrap">
    <div class="section-head">
      <p class="label">What we do</p>
      <h2 id="svc-h">One company for the whole yard</h2>
      <p class="lede">Most yard projects need more than one trade. We fix the water, move the dirt and finish the landscape, so you're not coordinating three different contractors.</p>
    </div>
    <div class="svc-list">{rows}</div>
  </div>
</section>

<section class="section" id="work" aria-labelledby="work-h">
  <div class="wrap">
    <div class="section-head">
      <p class="label">Before &amp; after</p>
      <h2 id="work-h">Real jobs from around Utah County</h2>
      <p class="lede">Every photo on this site is from our own projects.</p>
    </div>
    <div class="ba-grid">{ba}</div>
    <div style="margin-top:clamp(28px,4vw,44px)">{gal}</div>
  </div>
</section>
{rebate_section(calc_href=link(COST_SLUG) + "#rebate-calculator")}
{reviews_section(["brandon", "mason", "joshua", "kasha", "aaron", "bryce"])}
{steps_section()}
{area_section()}
{faq}
</main>
{cta_band()}'''

def service_hero(crumb, label, h1, lede, photo, alt, caption, link):
    return f'''
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="crumbs"><a href="{link("")}">Home</a> / {crumb}</p>
      <p class="label">{label}</p>
      <h1>{h1}</h1>
      <p class="lede">{lede}</p>
      {cta_buttons()}
      {proof()}
    </div>
    <figure class="hero-photo" style="margin:0">
      {img(photo, alt, "(max-width: 860px) 100vw, 46vw", eager=True)}
      <figcaption>{caption}</figcaption>
    </figure>
  </div>
</section>'''

def page_sprinklers(link):
    symptoms = ["Water shooting up from a broken head", "Brown, dry patches even though the system runs",
                "A zone that won't turn on, or won't shut off", "Water pooling around a valve box",
                "Low pressure, or heads that barely pop up", "Overspray hitting the sidewalk, driveway or house"]
    return f'''
<main id="main">
{service_hero("Sprinkler repair", "Sprinklers &amp; irrigation", 'Sprinkler repair in <span class="hl">Springville &amp; Utah County</span>',
   "Broken heads, leaking valves, zones that won't shut off, water bubbling up in the yard. We're a Springville sprinkler repair company working across Utah County. We find the problem, fix it right, and check that every zone covers the way it should.",
   "broken-sprinkler-head-repair", "Broken sprinkler head spraying water onto a park strip and sidewalk", "Broken head flooding a park strip", link)}

<section class="section section-alt" aria-labelledby="sym-h">
  <div class="wrap split">
    {img("sprinkler-valve-box-repair", "Sprinkler valve box with a rebuilt three-valve manifold", "(max-width: 860px) 100vw, 50vw")}
    <div class="split-copy">
      <p class="label">Sound familiar?</p>
      <h2 id="sym-h">Signs your sprinklers need a repair</h2>
      <ul class="checks">{"".join(f"<li>{s}</li>" for s in symptoms)}</ul>
      <p>Text a photo or short video of the problem to <a class="textlink" href="sms:{PHONE_TEL}">{PHONE_DISPLAY}</a>. It helps us show up with the right parts.</p>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="fix-h">
  <div class="wrap">
    <div class="section-head"><p class="label">What we fix</p><h2 id="fix-h">Sprinkler &amp; irrigation services</h2></div>
    {fixes([
        ("Heads &amp; rotors", "Replace broken, sunken or tilted heads and rotors, and change nozzles to even out coverage."),
        ("Valves &amp; manifolds", "Repair or replace leaking and stuck valves, rebuild manifolds, and fix flooded valve boxes."),
        ("Line breaks &amp; leaks", "Dig out and repair broken pipe and fittings, including leaks you can't see from the surface."),
        ("Pressure &amp; coverage", "Track down low pressure and dry spots, then adjust heads and spacing so the whole lawn gets water."),
        ("Drip irrigation", "Install drip for flower beds, trees and shrubs, or convert spray zones over to drip."),
        ("Upgrades &amp; adjustments", "Add heads, replace worn parts with more efficient ones, and set a watering schedule that fits the season."),
        ("Spring start-ups", "Water back on, every zone run and checked, heads adjusted and the controller set for the season, with any winter damage found before summer."),
        ("Fall blowouts", f'Every zone cleared with compressed air before the hard freezes. <a class="textlink" href="{link("sprinkler-blowout-in-utah-county")}">About blowouts</a>'),
    ])}
    <div style="margin-top:clamp(28px,4vw,44px)" id="pricing">
      <h3 style="margin:0 0 12px">Sprinkler repair pricing</h3>
      <div class="prices">
        <div class="price"><span class="what">Coming out to take a look<small>We find the problem and tell you what it should cost</small></span><span class="amt">Free</span></div>
        <div class="price price-total"><span class="what">Repair labor<small>If you decide to go ahead</small></span><span class="amt">${REPAIR_RATE} / hour</span></div>
        <div class="price"><span class="what">Minimum<small>Once the repair starts</small></span><span class="amt">1 hour</span></div>
        <div class="price"><span class="what">Parts<small>Heads, valves, pipe and fittings, based on what the repair needs</small></span><span class="amt">Extra</span></div>
      </div>
      <p class="source">No work starts until you say yes.</p>
    </div>
    <div style="margin-top:clamp(28px,4vw,44px)">{gallery([
        ("sprinkler-valve-manifold-install", "Three-valve sprinkler manifold assembled before burial", "New valve manifold"),
        ("sprinkler-valve-box-service", "Opened sprinkler valve box ready for service", "Valve box service"),
        ("green-lawn-after-sprinkler-repair", "Healthy green backyard lawn with even sprinkler coverage", "Even coverage after repair"),
    ])}</div>
  </div>
</section>

<section class="section section-alt" aria-labelledby="trouble-h">
  <div class="wrap">
    <div class="section-head">
      <p class="label">Troubleshooting</p>
      <h2 id="trouble-h">Common sprinkler problems and what usually causes them</h2>
      <p class="lede">Many Utah County homes water with secondary water (pressurized irrigation). It isn't filtered like tap water, so sand and grit are a common cause of clogged nozzles and valves that won't close.</p>
    </div>
    {fixes([
        ("Water bubbling up or a soggy spot", "Usually a cracked pipe or fitting, or a leaking valve. If the spot stays wet with the sprinklers off, the leak is probably on the main line, which is under pressure all the time. Shut off the water to the sprinkler system and text us a photo."),
        ("A zone won't turn on", "Often a bad solenoid, a broken wire or a controller problem. If you can hear the valve click but no water comes out, the valve itself or the water supply is the more likely cause."),
        ("A zone won't shut off", "Usually grit or a torn diaphragm holding the valve open. This one wastes a lot of water fast, so turn off the water to the system until it's fixed."),
        ("Low pressure or heads that barely pop up", "A break somewhere on the zone, a partly closed valve, a clogged filter or nozzles, or too many heads on one zone."),
        ("Brown or dry spots", "Clogged or mismatched nozzles, sunken or tilted heads, or heads blocked by grass and plants. Older systems often have spots the spacing never reached."),
        ("Water hitting the sidewalk or house", "Heads that are misaligned, broken or the wrong spray pattern. Fixing overspray saves water and keeps it away from the foundation."),
    ])}
    <p style="margin-top:20px">Not sure which one it is? Text a photo or short video to <a class="textlink" href="sms:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>
  </div>
</section>
{rebate_section(compact=True)}
{reviews_section(["mason", "kasha", "joshua"], "Utah County's sprinkler guy")}
{area_section()}
{faq_section([
    ("How fast can you come out?", "We answer calls and texts the same day and get repairs on the schedule as soon as we can. Texting a photo of the problem helps us bring the right parts the first time."),
    ("How much does sprinkler repair cost?", f"Coming out to look is free. If you go ahead, repairs are ${REPAIR_RATE} an hour plus parts, with a 1-hour minimum. A broken head or nozzle is usually quick. Line breaks and valve replacements take more digging, parts and time. You'll know what it should cost before any work starts."),
    ("Why is water bubbling up in my yard?", "Most of the time it's a broken pipe or fitting underground, or a leaking valve. If the spot stays wet with the sprinklers off, the leak is probably on the main line, which is under pressure all the time. Turn off the water to the sprinkler system and text us a photo."),
    ("Can you fix a system someone else installed?", "Yes. We repair sprinkler systems no matter who put them in."),
    ("Do you work on systems that run on secondary water?", "Yes. Secondary water isn't filtered, so sand and grit can clog nozzles and keep valves from closing. We clean or replace what's clogged and can add a filter where it helps."),
    ("Do you work on drip systems?", "Yes. We repair drip lines and emitters, add drip to beds and trees, and convert spray zones to drip."),
    ("Where do you do sprinkler repair?", "Springville, Mapleton, Spanish Fork, Salem, Payson, Provo, Orem and nearby. Outside that area? Text us and ask."),
    ("Do you do fall blowouts?", f'Yes. We blow out every zone with compressed air before the hard freezes. See <a class="textlink" href="{link("sprinkler-blowout-in-utah-county")}">sprinkler blowouts</a>.'),
])}
</main>
{cta_band("Sprinklers acting up? Let's fix them.", f"Free look, then ${REPAIR_RATE} an hour plus parts if you go ahead. Call or text Sergio, Monday to Saturday, 8am to 6pm.")}'''

def page_xeriscape(link):
    return f'''
<main id="main">
{service_hero("Xeriscaping", "Low-water landscaping", 'Xeriscaping &amp; low-water yards <span class="hl">in Utah County</span>',
   "Less mowing, lower water bills, and a yard that still looks finished. We're a Springville xeriscaping company building water-wise yards across Utah County: rock, drought-tolerant plants, drip irrigation, park strip conversions, and as much or as little lawn as you want to keep.",
   "xeriscape-side-yard-sod-rock-border", "Side yard with a small lawn framed by rock and drought-tolerant grasses", "Lawn reduction with rock borders", link)}

<section class="section section-alt" aria-labelledby="xfix-h">
  <div class="wrap">
    <div class="section-head"><p class="label">What we install</p><h2 id="xfix-h">What goes into a low-water yard</h2></div>
    {fixes([
        ("Full xeriscape installs", "Complete low-water yard transformations, from turf removal and grading to the finished landscape."),
        ("Decorative rock &amp; gravel", "Rock and gravel beds, borders and ground cover that hold up to Utah summers and winters."),
        ("Sod &amp; lawn reduction", "Keep a smaller, easier lawn where you actually use it, and replace the rest with water-wise landscaping."),
        ("Drip irrigation", "Drip lines to plants, trees and beds, so water goes to roots instead of rock."),
        ("Concrete curbing &amp; edging", "Clean edges between lawn, rock and beds that keep materials where they belong."),
        ("Planting &amp; layout", "Drought-tolerant plants placed so the yard looks planned, not empty."),
    ])}
  </div>
</section>

<section class="section" id="park-strips" aria-labelledby="strip-h">
  <div class="wrap split">
    {img("broken-sprinkler-head-repair", "Broken sprinkler head spraying water onto a park strip and sidewalk", "(max-width: 860px) 100vw, 50vw")}
    <div class="split-copy">
      <p class="label">Park strips</p>
      <h2 id="strip-h">Park strip conversions</h2>
      <p>The park strip is the narrow strip of grass between the sidewalk and the street. It's the hardest part of a yard to water well. Spray heads hit the sidewalk and curb, and a lot of that water runs down the gutter. Swapping it for rock, mulch and low plants on drip is one of the quickest ways to cut outdoor water use.</p>
      <p>Park strips qualify for the lawn-replacement rebate, with a few extra rules: plants under 24 inches, no rebate trees in narrow strips, and a 200 sq ft project minimum that most people meet by pairing the strip with part of the front lawn.</p>
      <p><a class="textlink" href="{link(STRIP_SLUG)}">Park strip rules, plant ideas and costs</a></p>
    </div>
  </div>
</section>

<section class="section section-alt" aria-labelledby="plants-h">
  <div class="wrap">
    <div class="section-head">
      <p class="label">Xeriscape ideas</p>
      <h2 id="plants-h">Low-water plants that do well in Utah County</h2>
      <p class="lede">Plants are what keep a xeriscape from looking like a gravel lot. These handle hot, dry summers, cold winters and alkaline soil once they're established on drip.</p>
    </div>
    {fixes([
        ("Penstemon", "Utah natives with tall spikes of red, pink, blue or purple flowers in late spring. Hummingbirds love them."),
        ("Russian sage &amp; catmint", "Soft purple-blue color for most of the summer. Tough in heat and rarely bothered by deer."),
        ("Lavender &amp; agastache", "Fragrant, long-blooming and loved by pollinators. Agastache is also called hummingbird mint."),
        ("Ornamental grasses", "Blue grama and blue avena grass add movement and look good through the winter."),
        ("Ground covers", "Creeping thyme, hardy ice plant and sedum fill in between stepping stones and soften rock beds."),
        ("Native shrubs", "Apache plume and rabbitbrush give structure and need very little water once they're settled in."),
    ])}
  </div>
</section>

<section class="section" aria-labelledby="xwork-h">
  <div class="wrap">
    <div class="section-head"><p class="label">Our work</p><h2 id="xwork-h">Water-wise yards we've built</h2></div>
    <div class="ba-grid">
      <div class="ba">
        <div class="ba-pair">
          <figure>{img("xeriscape-rock-yard-before", "Front yard stripped to bare dirt before a xeriscape install", "(max-width: 760px) 50vw, 25vw")}<span class="tag">Before</span></figure>
          <figure>{img("xeriscape-rock-yard-after", "Same front yard finished with rock landscaping around a mature tree", "(max-width: 760px) 50vw, 25vw")}<span class="tag after">After</span></figure>
        </div>
        <h3>Lawn to rock xeriscape</h3>
        <p>Old lawn and soil removed, grade set, and rock installed around the existing shade tree.</p>
      </div>
      <div class="ba">
        <figure style="margin:0">{img("lawn-with-rock-border-xeriscape", "Front lawn with concrete curbing, rock borders and ornamental grasses", "(max-width: 760px) 100vw, 50vw")}</figure>
        <h3>Smaller lawn, rock borders</h3>
        <p>A lawn sized for real use, framed with curbing, rock and drought-tolerant grasses.</p>
      </div>
    </div>
    <div style="margin-top:clamp(28px,4vw,44px)">{gallery([
        ("drip-irrigation-planting-bed", "Mulched planting bed with drip irrigation along a stone wall", "Drip-irrigated bed"),
        ("sod-and-rock-front-yard-utah-county", "Front yard with new sod, rock borders and grasses", "Sod and rock front yard"),
        ("new-sod-backyard", "Backyard with fresh sod next to a deck", "Fresh sod backyard"),
    ])}</div>
  </div>
</section>
{rebate_section(calc_href="#rebate-calculator")}
{calculator_section()}
{reviews_section(["brandon", "aaron", "joshua"], "Built with care")}
{area_section()}
{faq_section([
    ("How much does xeriscaping cost?", f'Most full conversions in Utah run about ${COST_LOW} to ${COST_HIGH} per square foot before rebates. See <a class="textlink" href="{link(COST_SLUG)}">xeriscaping costs in Utah County</a> for typical prices and a worked example.'),
    ("Will a xeriscape yard just look like a gravel lot?", "It doesn't have to. A good xeriscape mixes rock, plants, edging and often some lawn, so the yard looks planned and finished."),
    ("Can I keep some grass?", "Yes. Plenty of our projects keep a smaller lawn with rock borders and drip-watered beds around it."),
    ("How does the lawn-replacement rebate work?", "You apply through Utah Water Savers, and the program visits and approves the project before any grass comes out. Spanish Fork, Salem and Payson pay $3.00 per sq ft; Springville, Mapleton, Provo and Orem pay $1.50. We measure, photograph and draw the plan the application needs, then build the yard to the program's rules."),
    ("Does the rebate cover park strips?", f'Yes, at the same per-square-foot rate as the rest of the lawn, with extra rules on plant height and trees. See <a class="textlink" href="{link(STRIP_SLUG)}">park strip landscaping</a>.'),
    ("What plants work best for xeriscaping in Utah?", "Plants that handle heat, cold and alkaline soil once they're established, like penstemon, Russian sage, catmint, lavender, agastache, blue grama grass, and ground covers such as creeping thyme and hardy ice plant. We put them on drip so each one gets water at the roots."),
    ("Can I apply for the rebate in winter?", "You can plan and design now, but in towns with secondary water the program's site visits pause from October 15 to April 15. We'll have your plan ready so you can apply as soon as visits start again."),
    ("What happens to my sprinklers?", "We cap or convert the spray zones under the new landscape and run drip to the plants, so you only water what needs it."),
    ("Do you handle the dirt work too?", "Yes. Turf removal, grading and prep are part of the job. You don't need a separate excavation company."),
])}
</main>
{cta_band("Ready to cut your water bill?")}'''

def page_excavation(link):
    return f'''
<main id="main">
{service_hero("Excavation", "Excavation &amp; site prep", 'Excavation &amp; grading <span class="hl">in Utah County</span>',
   "The work under the finished project: digging, grading, trenching, and prep for concrete, drainage and retaining walls. We work with compact equipment built for residential yards.",
   "excavation-from-excavator-cab", "View from an excavator cab digging a deep residential excavation", "Excavation from the cab", link)}

<section class="section section-alt" aria-labelledby="efix-h">
  <div class="wrap">
    <div class="section-head"><p class="label">What we do</p><h2 id="efix-h">Excavation &amp; site prep services</h2></div>
    {fixes([
        ("Grading &amp; leveling", "Set the grade for lawns, patios and landscapes so water drains away from the house."),
        ("Trenching", "Trenches for irrigation, drainage, utilities and landscape lines."),
        ("Concrete prep", "Dig-out, forms and compacted base for patios, walkways, pads, curbing and driveway extensions."),
        ("Drainage prep", "Grading and trenching to move water where it should go."),
        ("Retaining wall prep", "Excavation and base work for landscape and boulder retaining walls."),
        ("Demo &amp; removal", "Remove old concrete, soil, grass and rock to clear the way for the new project."),
    ])}
  </div>
</section>

<section class="section" aria-labelledby="seq-h">
  <div class="wrap">
    <div class="section-head"><p class="label">Concrete prep, start to finish</p><h2 id="seq-h">A driveway extension in three steps</h2><p class="lede">The concrete only lasts as long as what's under it.</p></div>
    <div class="seq">
      <figure>{img("concrete-prep-excavation", "Compact track loader digging out a side yard", "(max-width: 640px) 100vw, 33vw")}<figcaption><b>Step 1 · Dig out</b>Old soil removed to the right depth.</figcaption></figure>
      <figure>{img("concrete-prep-compaction", "Plate compactor packing gravel base next to a driveway", "(max-width: 640px) 100vw, 33vw")}<figcaption><b>Step 2 · Base &amp; compaction</b>Road base spread and compacted.</figcaption></figure>
      <figure>{img("finished-concrete-driveway-extension", "Finished concrete driveway extension along a fence", "(max-width: 640px) 100vw, 33vw")}<figcaption><b>Step 3 · Finished</b>Concrete on a solid, level base.</figcaption></figure>
    </div>
    <div style="margin-top:clamp(28px,4vw,44px)">{gallery([
        ("concrete-pad-pour-crew", "Crew finishing a new concrete pad with mountains behind", "Concrete pad"),
        ("excavator-trenching", "Excavator digging a trench at a new home site", "Trenching"),
        ("excavation-next-to-house", "Deep excavation beside a house with a skid steer nearby", "Excavation beside a home"),
        ("boulder-wall-skid-steer", "Skid steer setting boulders for a rock wall", "Boulder wall"),
        ("grading-with-mini-excavator", "Mini excavator grading a residential lot", "Grading"),
        ("crew-removing-concrete", "Crew breaking out and removing old concrete", "Concrete removal"),
    ])}</div>
  </div>
</section>
{reviews_section(["aaron", "brandon", "joshua"], "Solid work, done right")}
{area_section()}
{faq_section([
    ("What size jobs do you take on?", "Mostly residential: yards, side yards, driveway extensions, pads, trenches and retaining wall prep. Larger projects can go anywhere along the Wasatch Front."),
    ("Can you get equipment into my backyard?", "We use compact equipment like mini excavators and skid steers for residential work. Send a photo of your gate or side yard and we'll tell you what fits."),
    ("Will you prep for my concrete or landscape contractor?", "Yes. We do the dig-out, grading and base so the next trade starts on a solid, level base."),
    ("Do underground utilities get marked first?", "Yes. Before any digging, buried lines are marked through Blue Stakes of Utah, the state's 811 service."),
    ("Are estimates free?", "Yes. Text photos of the area and we'll set up a time to look at it in person."),
])}
</main>
{cta_band("Need dirt moved?")}'''

def page_blowout(link):
    breaks = ["PVC pipe and fittings", "Valve bodies and diaphragms", "The backflow preventer, which sits above ground",
              "Sprinkler heads and risers", "Drip filters and pressure reducers"]
    return f'''
<main id="main">
{service_hero("Sprinkler blowouts", "Fall winterizing", 'Sprinkler blowouts &amp; winterization <span class="hl">in Utah County</span>',
   "Water left in your lines freezes, expands and cracks pipe, fittings and valves. We blow out every zone with compressed air before the hard freezes, so your system starts clean in spring.",
   "sprinkler-valve-box-service", "Opened sprinkler valve box with valves and wiring", "Valve box service · Utah County", link)}

<section class="section section-alt" aria-labelledby="when-h">
  <div class="wrap split">
    {img("green-lawn-after-sprinkler-repair", "Healthy green backyard lawn with even sprinkler coverage", "(max-width: 860px) 100vw, 50vw")}
    <div class="split-copy">
      <p class="label">Timing</p>
      <h2 id="when-h">After the water's off, before the hard freeze</h2>
      <p>Springville City shuts off pressurized irrigation around October 15. Other cities set their own dates, so check yours. Turning the water off doesn't empty the pipes: water still sits in the lines, valves and backflow preventer, and that's what freezes.</p>
      <p><b>What a frozen line can break:</b></p>
      <ul class="checks">{"".join(f"<li>{b}</li>" for b in breaks)}</ul>
      <p>Text your address and how many zones you have, if you know, to <a class="textlink" href="sms:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="bfix-h">
  <div class="wrap">
    <div class="section-head"><p class="label">What's included</p><h2 id="bfix-h">How we winterize your system</h2></div>
    {fixes([
        ("Shut the system down", "Water to the sprinkler system off, and the controller set so it won't try to run all winter."),
        ("Clear every zone", "Compressed air through one zone at a time until the heads stop spitting water."),
        ("Keep pressure safe", "Air pressure kept in the safe range for your pipe, no more than about 80 psi for PVC and 50 psi for poly. Too much pressure is how pipes get split."),
        ("Drip zones too", "Drip lines, filters and pressure reducers get cleared as well, at lower pressure."),
        ("Protect the backflow", "The backflow preventer sits above ground, so it's usually the first part to crack in a freeze. We make sure it's empty."),
        ("Notes for spring", "If we spot a broken head, a leak or a bad valve while we're there, we tell you so it gets fixed before the season starts."),
    ])}
  </div>
</section>
{reviews_section(["mason", "kasha", "bryce"], "Utah County's sprinkler guy")}
{area_section()}
{faq_section([
    ("When should I get my sprinklers blown out?", "After your city shuts off secondary water and before the first hard freeze. In Springville the water goes off around October 15."),
    ("My secondary water is already off. Do I still need a blowout?", "Yes. Shutting off the water doesn't drain the pipes. Water left in the lines, valves and backflow preventer can still freeze and crack them."),
    ("Can I do it myself with a shop compressor?", "Most home compressors can't move enough air to clear a full zone, and too much pressure can split pipe. A large compressor clears the lines faster and more safely."),
    ("What do you need from me?", "Your address, access to the valve boxes, backflow preventer and controller, and the number of zones if you know it."),
    ("Do you turn the system back on in spring?", "Yes, with our spring start-up service: water back on, every zone run and checked, heads adjusted and the controller set for the season. Ask for it when we do your blowout and you'll be on our spring list."),
])}
</main>
{cta_band("Beat the first hard freeze.")}'''

COST_SLUG = "xeriscaping-cost-utah-county"

def page_cost(link):
    lo, hi = 1000 * COST_LOW, 1000 * COST_HIGH
    ex_rows = (f'<div class="price"><span class="what">Typical cost, 1,000 sq ft</span><span class="amt">${lo:,}–${hi:,}</span></div>'
               f'<div class="price"><span class="what">Rebate in Spanish Fork, Salem or Payson<small>$3.00 per sq ft</small></span><span class="amt">−$3,000</span></div>'
               f'<div class="price price-total"><span class="what">Your cost after the rebate</span><span class="amt">${lo-3000:,}–${hi-3000:,}</span></div>'
               f'<div class="price"><span class="what">Rebate in Springville, Mapleton, Provo or Orem<small>$1.50 per sq ft</small></span><span class="amt">−$1,500</span></div>'
               f'<div class="price price-total"><span class="what">Your cost after the rebate</span><span class="amt">${lo-1500:,}–${hi-1500:,}</span></div>')
    return f'''
<main id="main">
{service_hero("Xeriscaping cost", "2026 prices &amp; rebates", 'How much does xeriscaping cost <span class="hl">in Utah County?</span>',
   f"Most full xeriscape conversions in Utah run about ${COST_LOW} to ${COST_HIGH} per square foot, so roughly ${lo:,} to ${hi:,} for a 1,000 sq ft lawn. Utah County homeowners can get $1.50 to $3.00 per square foot back through the state's lawn-replacement rebate.",
   "xeriscape-rock-yard-after", "Front yard finished with rock landscaping around a mature tree", "Lawn to rock xeriscape · Utah County", link)}

<section class="section section-alt" aria-labelledby="inc-h">
  <div class="wrap">
    <div class="section-head">
      <p class="label">What you're paying for</p>
      <h2 id="inc-h">What goes into a xeriscape job</h2>
      <p class="lede">Every yard is different, so we don't price by the square foot. We look at the yard, talk through what you want, and give you one clear price before any work starts.</p>
    </div>
    {fixes([
        ("Lawn removal", "Cutting out the old sod and hauling it away, so nothing grows back through the rock."),
        ("Grading &amp; prep", "Setting the grade so water drains away from the house, then prepping the ground for rock and plants."),
        ("Sprinkler changes", "Capping the spray zones under the new landscape and running drip to every plant."),
        ("Rock, plants &amp; mulch", "Decorative rock, drought-tolerant plants and trees, laid out so the yard looks planned."),
        ("Edging &amp; curbing", "Clean borders between rock, beds and any lawn you keep."),
        ("Rebate paperwork help", "Measurements, photos and a plan drawing for the Utah Water Savers application."),
    ])}
    <p class="source">Published 2026 cost guides put full xeriscape conversions in Utah at about ${COST_LOW} to ${COST_HIGH} per sq ft. Your price depends on what your yard needs.</p>
  </div>
</section>

<section class="section" aria-labelledby="factors-h">
  <div class="wrap">
    <div class="section-head"><p class="label">What moves the price</p><h2 id="factors-h">Why one yard costs more than another</h2></div>
    {fixes([
        ("How much lawn you keep", "Keeping a small lawn where the kids play costs less than converting every square foot, and it can still qualify for the rebate on the part you replace."),
        ("Plants vs. rock", "Rock covers ground for less than a planted bed, but the rebate needs half the new area planted, so most yards land on a mix."),
        ("Curbing, boulders &amp; edging", "Concrete curbing, boulders and steel edging make a yard look finished and add to the cost."),
        ("Dirt work &amp; access", "Steep grades, poor drainage or a tight side gate mean more excavation time. We do this work ourselves, so there's no second contractor to pay."),
        ("Your sprinkler system", "Every job caps spray zones and runs drip to the new plants. A system already in good shape keeps that part of the cost down."),
        ("Size", "Bigger areas cost more in total but usually less per square foot, since setup and equipment are spread over more ground."),
    ])}
  </div>
</section>

{calculator_section(alt=True)}

<section class="section" aria-labelledby="ex-h">
  <div class="wrap">
    <div class="section-head">
      <p class="label">Example</p>
      <h2 id="ex-h">A 1,000 sq ft front lawn, before and after the rebate</h2>
      <p class="lede">Same yard, two towns. The rebate rate depends on where you live.</p>
    </div>
    <div class="prices">{ex_rows}</div>
    <p class="source">Rebate rates from the Utah Water Savers residential program pages, October 2026. Rates and rules can change.</p>
  </div>
</section>
{reviews_section(["brandon", "joshua", "aaron"], "Fair prices, honest work")}
{faq_section([
    ("How much does xeriscaping cost per square foot in Utah?", f"Most full conversions run about ${COST_LOW} to ${COST_HIGH} per square foot. A simple yard with rock and light planting sits at the low end. Curbing, boulders, dense planting and big grade changes push it higher."),
    ("How much does it cost to replace a 1,000 sq ft lawn?", f"Typically ${lo:,} to ${hi:,} before rebates. In Spanish Fork, Salem and Payson the lawn-replacement rebate is $3.00 per sq ft, or $3,000. In Springville, Mapleton, Provo and Orem it's $1.50 per sq ft, or $1,500."),
    ("Does the rebate pay for the whole project?", "No. It covers part of the cost. The program also has rules: it has to approve the project before any grass comes out, half the new area has to be planted, and artificial turf, concrete and pavers don't qualify."),
    ("Does a backyard cost more than a front yard?", "Mostly it comes down to access. If our equipment fits through the gate, a backyard prices about the same as a front yard of the same size. A tight gate or steep side yard means more hand work and more time."),
    ("How much does it cost to xeriscape a park strip?", f'Park strips are small, so setup and hauling make up a bigger share of the job, and the price per square foot usually lands toward the high end. The lawn-replacement rebate covers park strips too. See <a class="textlink" href="{link(STRIP_SLUG)}">park strip landscaping</a>.'),
    ("Is rock cheaper than sod?", "Up front they can cost about the same, depending on the rock and the yard. The difference is what comes after: rock and drip-watered plants don't need mowing and use far less water every summer."),
    ("Are estimates free?", "Yes. Call or text and we'll come look at the yard. You get a clear price before any work starts."),
    ("When should I start planning?", "Winter. In towns with secondary water, the rebate program's site visits pause from October 15 to April 15. If your plan and measurements are ready, you can apply as soon as visits start again in spring."),
])}
</main>
{cta_band("Want a real number for your yard?")}'''

STRIP_SLUG = "park-strip-landscaping-utah-county"

def page_parkstrip(link):
    rules = [
        "Approved before any grass comes out, and the lawn has to be alive at the first visit",
        "At least 200 sq ft in total. Areas can be combined, so a park strip can be paired with part of the front lawn",
        "Plants cover at least half the strip at maturity, and none grow taller than 24 inches",
        "3 to 4 inches of rock or mulch. Rubber mulch isn't allowed",
        "Drip on its own zone with a filter and pressure reducer. No micro-sprays, bubblers or soaker hoses",
        "No rebate trees in park strips narrower than 10 feet",
        "No leftover strip of lawn narrower than 8 feet",
    ]
    return f'''
<main id="main">
{service_hero("Park strips", "Park strip conversions", 'Park strip landscaping <span class="hl">in Utah County</span>',
   "Turn the strip of grass between the sidewalk and the street into rock, mulch and low-water plants on drip. We plan it to the rebate program's rules, do the dirt work and the sprinkler changes, and help with the application.",
   "broken-sprinkler-head-repair", "Broken sprinkler head spraying water onto a park strip and sidewalk", "Spray heads in a park strip water the sidewalk too", link)}

<section class="section section-alt" aria-labelledby="why-h">
  <div class="wrap">
    <div class="section-head">
      <p class="label">Why start here</p>
      <h2 id="why-h">The park strip is the easiest lawn to give up</h2>
    </div>
    {fixes([
        ("Spray can't water it well", "Sprinklers aren't designed for areas narrower than about 8 feet. In a park strip, a lot of the water lands on the sidewalk and runs down the gutter."),
        ("Nobody uses it", "It still needs mowing, edging and water every week, but nobody plays or sits on it."),
        ("Everyone sees it", "It's the first thing people see from the street. A clean, planted strip makes the whole yard look finished."),
    ])}
  </div>
</section>

<section class="section" aria-labelledby="rules-h">
  <div class="wrap split">
    {img("drip-irrigation-planting-bed", "Mulched planting bed with drip irrigation along a stone wall", "(max-width: 860px) 100vw, 50vw")}
    <div class="split-copy">
      <p class="label">Rebate rules</p>
      <h2 id="rules-h">What the Utah County rebate requires for park strips</h2>
      <p>Park strips go through Central Utah Water's Landscape Incentive Program on Utah Water Savers. These are the rules that matter most:</p>
      <ul class="checks">{"".join(f"<li>{r}</li>" for r in rules)}</ul>
      <p>The rate depends on your town. Springville, Mapleton, Provo and Orem pay $1.50 per sq ft of lawn replaced. Spanish Fork, Salem and Payson pay $3.00. <a class="textlink" href="{link(COST_SLUG)}#rebate-calculator">Estimate your rebate</a></p>
      <p class="fine">From the Central Utah Water program pages on Utah Water Savers, October 2026. Rules can change, and your city may have its own park strip rules.</p>
    </div>
  </div>
</section>

<section class="section section-alt" aria-labelledby="how-h">
  <div class="wrap">
    <div class="section-head"><p class="label">How we do it</p><h2 id="how-h">How we convert a park strip</h2></div>
    {fixes([
        ("Measure &amp; plan", "We measure the strip, take the photos and draw the 2D plan the rebate application asks for."),
        ("Approval visit", "The program visits and approves the project before any grass comes out."),
        ("Turf out", "Sod removed and the strip dug down a few inches below the sidewalk, so rock and mulch stay in the strip."),
        ("Sprinkler changes", "Spray heads capped and a new drip zone added, with the filter and pressure reducer the program requires."),
        ("Plants &amp; mulch", "Low plants that stay under 24 inches, 3 to 4 inches of rock or mulch, and room by the curb to step out of a parked car."),
        ("Final inspection", "We run the drip with you so it's working and leak-free when the program comes back to sign off."),
    ])}
  </div>
</section>

<section class="section" aria-labelledby="splants-h">
  <div class="wrap">
    <div class="section-head">
      <p class="label">Park strip ideas</p>
      <h2 id="splants-h">Low plants that work in a Utah park strip</h2>
      <p class="lede">Park strips get full sun, reflected heat off the concrete and road salt in winter, and the rebate caps plants at 24 inches. These stay low and handle all of it.</p>
    </div>
    {fixes([
        ("Creeping thyme", "A flat, tough ground cover that fills in around stepping stones and smells good when you walk on it."),
        ("Sedum &amp; hardy ice plant", "Low succulents that spread between rocks and bloom in summer."),
        ("Blue fescue", "Small blue mounds of grass that look good year-round."),
        ("Pineleaf penstemon", "A low Utah-friendly penstemon with orange-red flowers that hummingbirds like."),
        ("Compact catmint", "Short varieties like Little Trudy give purple color most of the summer."),
        ("Kinnikinnick", "An evergreen ground cover for strips with some shade from street trees."),
    ])}
    <p class="source">We check the mature height of every plant against the 24-inch rule before it goes in.</p>
  </div>
</section>
{faq_section([
    ("How much does a park strip conversion cost?", f'Park strips are small, so setup and hauling make up a bigger share of the job, and the price per square foot usually lands toward the high end of the ${COST_LOW} to ${COST_HIGH} per sq ft range for xeriscaping. The rebate takes a real bite out of it. Estimates are free. See <a class="textlink" href="{link(COST_SLUG)}">xeriscaping costs in Utah County</a>.'),
    ("Does my park strip qualify for the rebate on its own?", "Only if it's at least 200 sq ft. Many aren't: a 6 by 30 foot strip is 180 sq ft. Areas can be combined to reach the minimum, so most people pair the park strip with part of the front lawn or a side yard."),
    ("Can I just put rock in my park strip?", "Not if you want the rebate. Plants have to cover at least half the strip at maturity. A mix of rock or mulch and low plants also looks better and stays cooler than solid rock."),
    ("Can I plant a tree in my park strip?", "The rebate doesn't pay for trees in park strips narrower than 10 feet. Cities also have their own rules for street trees, so check with yours before planting one."),
    ("Is this the same as Flip Your Strip?", "Flip Your Strip was the name of Central Utah Water's original park strip program, and Salt Lake County programs still use it. In Utah County today, park strips go through the Landscape Incentive Program on Utah Water Savers."),
    ("When should I do it?", "Plan it in winter. In towns with secondary water, the program's site visits pause from October 15 to April 15. With the plan and photos ready, you can apply as soon as visits start again in spring."),
])}
{area_section()}
</main>
{cta_band("Ready to get rid of the park strip lawn?")}'''

PAGES = [
    {"slug": "", "file": "index", "fn": page_home,
     "title": "Landscaping & Sprinkler Repair in Springville, UT | Vessel Groundworks",
     "desc": "Springville landscaping company serving Utah County: sprinkler repair, xeriscaping and excavation. 5.0 on Google, free estimates. Call or text (385) 398-9355.",
     "schema": [BUSINESS]},
    {"slug": "sprinkler-repair-in-utah-county", "file": "sprinkler-repair-in-utah-county", "fn": page_sprinklers,
     "title": "Sprinkler Repair in Springville & Utah County | Vessel Groundworks",
     "desc": f"Sprinkler repair in Springville, Provo, Orem, Spanish Fork and across Utah County. Free estimates, then ${REPAIR_RATE}/hour plus parts. Broken heads, valves, line breaks.",
     "schema": [dict(service_schema("Sprinkler repair", "sprinkler-repair-in-utah-county", "Sprinkler and irrigation repair in Springville and across Utah County: heads, valves, line breaks, pressure and coverage, drip."),
                     offers={"@type": "Offer", "priceCurrency": "USD", "priceSpecification": {"@type": "UnitPriceSpecification", "price": REPAIR_RATE, "priceCurrency": "USD", "unitCode": "HUR", "description": "Labor per hour, plus parts. 1-hour minimum."}}),
                breadcrumb("Sprinkler repair", "sprinkler-repair-in-utah-county")]},
    {"slug": "sprinkler-blowout-in-utah-county", "file": "sprinkler-blowout-in-utah-county", "fn": page_blowout,
     "title": "Sprinkler Blowouts & Winterization in Utah County | Vessel Groundworks",
     "desc": "Sprinkler blowouts and winterization in Springville, Spanish Fork, Provo, Orem and across Utah County. Every zone cleared with compressed air before the hard freeze.",
     "schema": [service_schema("Sprinkler blowout and winterization", "sprinkler-blowout-in-utah-county", "Fall sprinkler blowouts and irrigation winterizing across Utah County."), breadcrumb("Sprinkler blowouts", "sprinkler-blowout-in-utah-county")]},
    {"slug": "xeriscaping-in-utah-county", "file": "xeriscaping-in-utah-county", "fn": page_xeriscape,
     "title": "Xeriscaping in Utah County: Installs & Rebate Help | Vessel Groundworks",
     "desc": "Springville xeriscaping company serving Utah County. Rock, drought-tolerant plants, drip and park strip conversions, plus help with Utah's lawn-replacement rebate.",
     "schema": [service_schema("Xeriscaping and low-water landscaping", "xeriscaping-in-utah-county", "Xeriscape, park strip conversion and low-water landscape installation across Utah County."), breadcrumb("Xeriscaping", "xeriscaping-in-utah-county")]},
    {"slug": "excavation-in-utah-county", "file": "excavation-in-utah-county", "fn": page_excavation,
     "title": "Excavation & Grading in Utah County | Vessel Groundworks",
     "desc": "Residential excavation, grading, trenching and concrete prep in Springville and across Utah County. Compact equipment for tight yards. Free estimates.",
     "schema": [service_schema("Excavation, grading and site prep", "excavation-in-utah-county", "Residential excavation, grading, trenching and site prep across Utah County."), breadcrumb("Excavation", "excavation-in-utah-county")]},
    {"slug": COST_SLUG, "file": COST_SLUG, "fn": page_cost,
     "title": "Xeriscaping Cost in Utah County (2026) + Rebate Calculator | Vessel Groundworks",
     "desc": f"What xeriscaping costs in Utah County: about ${COST_LOW}–${COST_HIGH} per sq ft, plus $1.50–$3.00 per sq ft back from the lawn-replacement rebate. Free rebate calculator and estimates.",
     "schema": [breadcrumb("Xeriscaping cost", COST_SLUG)]},
    {"slug": STRIP_SLUG, "file": STRIP_SLUG, "fn": page_parkstrip,
     "title": "Park Strip Landscaping in Utah County + Rebate Rules | Vessel Groundworks",
     "desc": "Turn your park strip into rock, mulch and low-water plants on drip. Utah County rebate rules, plant ideas and installs by Vessel Groundworks in Springville.",
     "schema": [service_schema("Park strip landscaping", STRIP_SLUG, "Park strip conversions to water-wise landscaping with drip irrigation across Utah County."), breadcrumb("Park strips", STRIP_SLUG)]},
]

def build():
    # production
    prod_link = lambda s: "/" if s == "" else "/" + s
    for p in PAGES:
        body = header(p["slug"], prod_link) + p["fn"](prod_link) + footer(prod_link)
        with open(os.path.join(SITE, p["file"] + ".html"), "w") as f:
            f.write(full_doc(p, body))
    nf = {"slug": "", "title": "Page not found | Vessel Groundworks", "desc": "That page doesn't exist.", "schema": []}
    nf_body = (header("", prod_link) + '<main id="main"><section class="hero"><div class="wrap" style="display:grid;gap:20px;max-width:760px">'
               '<p class="label">Error 404</p><h1>That page isn\'t here</h1><p class="lede">The link may be old. Head back to the home page, or call or text us.</p>'
               + cta_buttons(second='<a class="btn btn-line" href="/">Home page</a>') + "</div></section></main>" + footer(prod_link))
    with open(os.path.join(SITE, "404.html"), "w") as f:
        f.write(full_doc(nf, nf_body).replace('<link rel="canonical" href="https://vesselgroundworks.com/">', '<meta name="robots" content="noindex">'))
    with open(os.path.join(SITE, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    urls = "".join(f"<url><loc>{DOMAIN}{prod_link(p['slug'])}</loc><lastmod>{LASTMOD}</lastmod></url>" for p in PAGES)
    with open(os.path.join(SITE, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')

    # preview (scratch workspace only)
    if REPO_MODE:
        print("built", [p["file"] for p in PAGES]); return
    if os.path.exists(PREVIEW):
        shutil.rmtree(PREVIEW)
    os.makedirs(PREVIEW)
    prev_link = lambda s: "index.html" if s == "" else s + ".html"
    for p in PAGES:
        body = header(p["slug"], prev_link) + p["fn"](prev_link) + footer(prev_link)
        if p["file"] == "index":
            frag = "<title>Vessel Groundworks</title>" + FONTS + f"<style>{CSS}</style>" + body
            with open(os.path.join(PREVIEW, "index.html"), "w") as f:
                f.write(frag)
        else:
            with open(os.path.join(PREVIEW, p["file"] + ".html"), "w") as f:
                f.write(full_doc(p, body))
    print("built", [p["file"] for p in PAGES])

if __name__ == "__main__":
    build()
