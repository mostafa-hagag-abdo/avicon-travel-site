<?php // site footer — CTA + tailor-made form + full avf footer ?>
<style>
.avi-tm{width:100%;padding:72px 24px;font-family:Poppins,Arial,sans-serif;box-sizing:border-box;position:relative;overflow:hidden;background:#fff}
.avi-tm *{box-sizing:border-box}
.avi-tm:before,.avi-tm:after{content:"";position:absolute;width:320px;height:320px;opacity:.08;pointer-events:none;background-image:radial-gradient(circle at 30% 30%,#f5a623 2px,transparent 2px);background-size:26px 26px}
.avi-tm:before{top:-40px;left:-60px}.avi-tm:after{bottom:-40px;right:-60px}
.avi-tm__wrap{position:relative;z-index:2;max-width:1150px;margin:0 auto}
.avi-tm__head{text-align:center;margin-bottom:42px}.avi-tm__deco{display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:16px}.avi-tm__deco span{height:1px;width:60px;background:linear-gradient(90deg,transparent,#f5a623)}.avi-tm__deco span:last-child{background:linear-gradient(90deg,#f5a623,transparent)}.avi-tm__deco i{font-size:28px;color:#f5a623}
.avi-tm__eyebrow{display:block;font-size:13px;font-weight:900;letter-spacing:0;text-transform:uppercase;color:#f5a623;margin-bottom:10px}.avi-tm__title{font-size:clamp(2rem,4.6vw,3rem);font-weight:900;color:#1a2547;line-height:1.18;margin:0 0 12px;letter-spacing:0}.avi-tm__title span{color:#1a4fc4}.avi-tm__sub{font-size:16px;color:#5a6275;line-height:1.7;max-width:650px;margin:0 auto}
.avi-tm__cols{display:grid;grid-template-columns:1.3fr .9fr;gap:36px;align-items:stretch}.avi-tm__card{background:#fff;border:1px solid rgba(26,37,71,.08);border-radius:18px;padding:34px;box-shadow:0 20px 50px rgba(26,37,71,.07)}.avi-tm__grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.avi-tm__field{display:flex;flex-direction:column}.avi-tm__field--full{grid-column:1/-1}.avi-tm__label{font-size:13px;font-weight:800;color:#1a2547;margin-bottom:8px}.avi-tm__input,.avi-tm__select,.avi-tm__textarea{width:100%;padding:14px 16px;border-radius:10px;border:1px solid #e1e4ed;background:#fcfcfd;color:#1a2547;font-family:Poppins,Arial,sans-serif;font-size:15px;outline:none;transition:all .22s ease}.avi-tm__input::placeholder,.avi-tm__textarea::placeholder{color:#9aa1b1}.avi-tm__input:focus,.avi-tm__select:focus,.avi-tm__textarea:focus{border-color:#f5a623;background:#fff;box-shadow:0 0 0 3px rgba(245,166,35,.12)}.avi-tm__select{appearance:none;cursor:pointer}.avi-tm__textarea{resize:vertical;min-height:120px}
.avi-tm__actions{display:flex;gap:14px;margin-top:26px;flex-wrap:wrap}.avi-tm__btn{flex:1;min-width:200px;display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:15px 24px;border-radius:999px;font-family:Poppins,Arial,sans-serif;font-size:15px;font-weight:900;border:0;cursor:pointer;transition:transform .22s ease,box-shadow .22s ease}.avi-tm__btn i{font-size:18px}.avi-tm__btn--send{background:linear-gradient(135deg,#1a4fc4,#123891);color:#fff;box-shadow:0 10px 25px rgba(26,79,196,.28)}.avi-tm__btn--wa{background:#25d366;color:#fff;box-shadow:0 10px 25px rgba(37,211,102,.26)}.avi-tm__btn:hover{transform:translateY(-3px)}.avi-tm__note{margin:16px 0 0;text-align:center;font-size:14px;font-weight:800;min-height:20px;color:#f5a623}
.avi-info{display:flex;flex-direction:column;gap:22px}.avi-info__image-wrap{width:100%;height:240px;border-radius:18px;overflow:hidden;box-shadow:0 15px 35px rgba(26,37,71,.1)}.avi-info__image-wrap img{width:100%;height:100%;object-fit:cover;transition:transform .45s ease}.avi-info__image-wrap:hover img{transform:scale(1.05)}.avi-info__box{background:#f7f8fb;border-radius:18px;padding:28px;border:1px solid #e1e4ed}.avi-info__title{font-size:22px;color:#1a2547;margin:0 0 18px;border-bottom:2px solid rgba(245,166,35,.32);padding-bottom:10px;display:inline-block;letter-spacing:0}.avi-info__list{list-style:none;padding:0;margin:0 0 22px;display:flex;flex-direction:column;gap:14px}.avi-info__list li{display:flex;align-items:flex-start;gap:12px;font-size:15px;color:#5a6275;line-height:1.55}.avi-info__list li i{width:24px;height:24px;color:#f5a623;flex-shrink:0;background:#fff;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 4px 10px rgba(245,166,35,.18)}.avi-info__contact{background:#fff;border-radius:14px;padding:18px;box-shadow:0 8px 20px rgba(26,37,71,.04)}.avi-info__contact-item{display:flex;align-items:center;gap:12px;margin-bottom:12px}.avi-info__contact-item:last-child{margin-bottom:0}.avi-info__contact-item i{width:20px;color:#1a4fc4}.avi-info__contact-item span{font-size:14px;color:#1a2547;font-weight:800}
@media(max-width:992px){.avi-tm__cols{grid-template-columns:1fr;gap:30px}.avi-info{order:-1}.avi-info__image-wrap{height:210px}}@media(max-width:600px){.avi-tm{padding:50px 16px}.avi-tm__card{padding:22px}.avi-tm__grid{grid-template-columns:1fr;gap:15px}.avi-tm__btn{min-width:100%}.avi-info__box{padding:22px}}
</style>
<section class="avi-tm" id="tailor-made-request">
  <div class="avi-tm__wrap">
    <div class="avi-tm__head">
      <div class="avi-tm__deco"><span></span><i class="fas fa-star"></i><span></span></div>
      <span class="avi-tm__eyebrow">Designed Around You</span>
      <h2 class="avi-tm__title">Tailor-Made Your <span>Egypt Journey</span></h2>
      <p class="avi-tm__sub">Tell us your dream trip and our local experts will craft a private, personalized itinerary just for you.</p>
    </div>
    <div class="avi-tm__cols">
      <div class="avi-tm__card">
        <form class="avi-tm__form" action="https://api.web3forms.com/submit" method="POST">
          <input type="hidden" name="access_key" value="7b1f50c3-489b-44ee-b413-d8c7a2e59c10">
          <input type="hidden" name="subject" value="New Tailor-Made Tour Request - Avicon">
          <input type="hidden" name="from_name" value="Avicon Website">
          <input type="checkbox" name="botcheck" style="display:none">
          <div class="avi-tm__grid">
            <div class="avi-tm__field"><label class="avi-tm__label">Full Name</label><input class="avi-tm__input" type="text" name="name" placeholder="Your full name" required></div>
            <div class="avi-tm__field"><label class="avi-tm__label">Email Address</label><input class="avi-tm__input" type="email" name="email" placeholder="you@example.com" required></div>
            <div class="avi-tm__field"><label class="avi-tm__label">Phone / WhatsApp</label><input class="avi-tm__input" type="tel" name="phone" placeholder="+20 ..." required></div>
            <div class="avi-tm__field"><label class="avi-tm__label">Destination</label><select class="avi-tm__select" name="destination"><option value="">Select a destination</option><option>Cairo</option><option>Luxor</option><option>Aswan</option><option>Hurghada</option><option>Sharm El Sheikh</option><option>Nile Cruise</option><option>Egypt Package</option><option>Day Tour</option><option>Multiple / Not sure</option></select></div>
            <div class="avi-tm__field"><label class="avi-tm__label">Travelers</label><input class="avi-tm__input" type="number" name="travelers" min="1" placeholder="e.g. 2" required></div>
            <div class="avi-tm__field"><label class="avi-tm__label">Travel Date</label><input class="avi-tm__input" type="date" name="date"></div>
            <div class="avi-tm__field avi-tm__field--full"><label class="avi-tm__label">Trip Details & Preferences</label><textarea class="avi-tm__textarea" name="message" placeholder="Tell us what you'd love to see, hotel preferences, cruise style, budget, or any special requests..."></textarea></div>
          </div>
          <div class="avi-tm__actions">
            <button type="submit" class="avi-tm__btn avi-tm__btn--send"><i class="fas fa-paper-plane"></i> Submit Request</button>
            <button type="button" class="avi-tm__btn avi-tm__btn--wa"><i class="fab fa-whatsapp"></i> Quick WhatsApp</button>
          </div>
          <p class="avi-tm__note" aria-live="polite"></p>
        </form>
      </div>
      <div class="avi-info">
        <div class="avi-info__image-wrap"><img decoding="async" src="/assets/uploads/2026/06/Avicon-Customer-Reviews-Pyramids-Giza.png" alt="Egypt Tour Experience"></div>
        <div class="avi-info__box">
          <h3 class="avi-info__title">Why Book With Us?</h3>
          <ul class="avi-info__list">
            <li><i class="fas fa-check"></i><span><strong>100% Customized:</strong> Tailor your itinerary to fit your interests, budget, and schedule.</span></li>
            <li><i class="fas fa-shield-alt"></i><span><strong>Local Experts:</strong> Guided by licensed Egyptologists who bring history to life.</span></li>
            <li><i class="fas fa-clock"></i><span><strong>24/7 Support:</strong> We are with you from the moment you land until departure.</span></li>
          </ul>
          <div class="avi-info__contact">
            <div class="avi-info__contact-item"><i class="fas fa-phone-alt"></i><span>+20 120 055 5600</span></div>
            <div class="avi-info__contact-item"><i class="fas fa-envelope"></i><span>info@avicontravel.com</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
<script>
(function(){
  document.querySelectorAll('.avi-tm__form').forEach(function(form){
    var note=form.querySelector('.avi-tm__note');
    var waBtn=form.querySelector('.avi-tm__btn--wa');
    function val(name){var el=form.querySelector('[name="'+name+'"]');return el?el.value.trim():'';}
    if(waBtn){waBtn.addEventListener('click',function(){
      var msg='Tailor-Made Tour Request - Avicon\n\n'+'Name: '+(val('name')||'-')+'\n'+'Email: '+(val('email')||'-')+'\n'+'Phone: '+(val('phone')||'-')+'\n'+'Destination: '+(val('destination')||'-')+'\n'+'Travelers: '+(val('travelers')||'-')+'\n'+'Date: '+(val('date')||'-')+'\n'+'Details: '+(val('message')||'-');
      window.open('https://wa.me/201200555600?text='+encodeURIComponent(msg),'_blank');
    });}
    form.addEventListener('submit',function(e){
      e.preventDefault();
      if(note){note.textContent='Sending your request...';}
      fetch('https://api.web3forms.com/submit',{method:'POST',body:new FormData(form)})
        .then(function(r){return r.json();})
        .then(function(res){if(res.success){if(note){note.textContent='Thank you! Our experts will contact you shortly.';}form.reset();}else{if(note){note.textContent='Something went wrong. Please try WhatsApp.';}}})
        .catch(function(){if(note){note.textContent='Network error. Please try WhatsApp.';}});
    });
  });
})();
</script>
<style>
.av-home{--primary:#123f7a;--primary-2:#1e90ff;--accent:#f6a13a;--ink:#10233d;--muted:#5d6b80;--soft:#f4f8fd;--line:#dbe6f2;--green:#1a9b77;--shadow:0 12px 32px rgba(16,35,61,.1);font-family:Poppins,Arial,sans-serif;color:var(--ink);background:#fff}
.av-home *{box-sizing:border-box}
.av-home a{text-decoration:none;color:inherit}
.av-home .container{max-width:1180px;margin:0 auto;padding:0 20px}
.av-home .btn{display:inline-flex;align-items:center;justify-content:center;gap:9px;min-height:44px;border-radius:8px;padding:11px 16px;font-size:14px;font-weight:900;transition:all .2s ease}
.av-home .btn.primary{background:var(--accent);color:#10233d}
.av-home .btn.secondary{background:#fff;color:var(--primary);border:1px solid var(--line)}
.av-home .btn:hover{transform:translateY(-2px)}
.av-home .cta{padding:44px 0;background:#10233d}
.av-home .cta-grid{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:center}
.av-home .cta h2{margin:0 0 8px;color:#fff;font-size:34px}
.av-home .cta p{margin:0;color:rgba(255,255,255,.84);line-height:1.7}
.av-home .cta-actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}
@media(max-width:992px){.av-home .cta-grid{grid-template-columns:1fr}.av-home .cta-actions{justify-content:flex-start}}
</style>
<div class="av-home">
<section class="cta">
    <div class="container">
      <div class="cta-grid">
        <div>
          <h2>Tailor-Made Egypt Tours by Avicon Travel</h2>
          <p>Tell Avicon Travel your destination, travel dates, group size, and preferred style, and get a custom Egypt itinerary covering packages, Nile cruises, day tours, transfers, or all of them together.</p>
        </div>
        <div class="cta-actions">
          <a class="btn primary" href="https://wa.me/201200555600" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i> WhatsApp</a>
          <a class="btn secondary" href="mailto:info@avicontravel.com"><i class="fas fa-envelope"></i> Email Us</a>
        </div>
      </div>
    </div>
  </section>
</div>
<style>
    /* ── TOKENS ── */
    .avf{
      --avf-blue:#1A4FC4; --avf-deep:#143a9e; --avf-bottom:#0f2d6b;
      --avf-gold:#F5A623; --avf-text:#eaf0ff; --avf-muted:#aebede;
      --avf-line:rgba(255,255,255,.12);
      background:linear-gradient(180deg,#1A4FC4 0%,#143a9e 55%,#0f2d6b 100%);
      color:var(--avf-text);
      font-family:'Nunito',system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
      font-size:15px; line-height:1.6;
      -webkit-font-smoothing:antialiased;
    }
    .avf *,.avf *::before,.avf *::after{box-sizing:border-box;}

    /* ── INNER CONTAINER ── */
    /* Desktop: max 1200px, comfortable padding */
    .avf__inner{max-width:1200px; margin:0 auto; padding:52px 40px 0;}

    /* ── TOP SECTION ── */
    /* Desktop: brand takes 58%, CTA takes 38% */
    .avf__top{
      display:grid; grid-template-columns:58% 38%; gap:4%;
      padding-bottom:40px; border-bottom:1px solid var(--avf-line);
      align-items:start;
    }
    .avf__tagline{margin:0 0 14px; color:var(--avf-muted); font-size:13.5px; line-height:1.65; max-width:48ch;}
    .avf__tagline strong{color:var(--avf-text); font-weight:700;}

    /* Find Us strip */
    .avf__findus{
      display:grid; grid-template-columns:1fr 280px; gap:28px; align-items:center;
      padding:22px 0; border-top:1px solid var(--avf-line);
    }
    .avf__findus-eyebrow{
      font-size:11px; letter-spacing:.14em; text-transform:uppercase;
      color:var(--avf-gold); font-weight:700;
    }
    .avf__findus-title{
      font-family:'Cinzel',serif; font-weight:600; font-size:16px;
      margin:5px 0 3px; color:#fff;
    }
    .avf__findus-line{margin:0 0 6px; color:var(--avf-muted); font-size:13px;}
    .avf__findus-link{
      color:var(--avf-gold); text-decoration:none; font-weight:700; font-size:12.5px;
      transition:opacity .2s ease;
    }
    .avf__findus-link:hover{opacity:.8;}
    .avf__map{border-radius:8px; overflow:hidden; line-height:0;}
    .avf__map iframe{height:130px;}
    .avf__addr{
      display:inline-flex; align-items:flex-start; gap:7px;
      color:var(--avf-text); text-decoration:none; font-weight:600;
      font-size:13px; line-height:1.5;
    }
    .avf__addr svg{flex:0 0 auto; margin-top:2px; color:var(--avf-gold);}
    .avf__addr:hover{color:var(--avf-gold);}
    .avf__social{display:flex; gap:10px; margin-top:18px;}
    .avf__social a{
      width:36px; height:36px; display:grid; place-items:center;
      border:1px solid var(--avf-line); border-radius:50%;
      color:var(--avf-text); transition:transform .2s ease,background .2s ease,color .2s ease,border-color .2s ease;
    }
    .avf__social a:hover{background:var(--avf-gold); color:#0f2d6b; border-color:var(--avf-gold); transform:translateY(-3px);}

    /* CTA card */
    .avf__cta{
      background:rgba(255,255,255,.06); border:1px solid var(--avf-line);
      border-radius:14px; padding:22px 24px;
    }
    .avf__cta-eyebrow{font-size:11px; letter-spacing:.13em; text-transform:uppercase; color:var(--avf-gold); font-weight:700;}
    .avf__cta-title{font-family:'Cinzel',serif; font-weight:600; font-size:18px; margin:5px 0 7px; color:#fff;}
    .avf__cta-text{color:var(--avf-muted); margin:0 0 16px; font-size:13px;}
    .avf__cta-btn{
      display:inline-flex; align-items:center; gap:8px;
      background:var(--avf-gold); color:#0f2d6b; font-weight:800; font-size:14px;
      padding:11px 18px; border-radius:9px; text-decoration:none;
      transition:transform .2s ease,box-shadow .2s ease;
    }
    .avf__cta-btn:hover{transform:translateY(-2px); box-shadow:0 8px 20px rgba(245,166,35,.3);}
    .avf__cta-lines{display:flex; flex-wrap:wrap; gap:5px 16px; margin-top:13px;}
    .avf__cta-lines a{color:var(--avf-text); text-decoration:none; font-weight:600; font-size:13px;}
    .avf__cta-lines a:hover{color:var(--avf-gold);}

    /* ── LINK COLUMNS ── */
    /* Desktop: 4 even columns */
    .avf__cols{display:grid; grid-template-columns:repeat(4,1fr); gap:32px; padding:40px 0;}
    .avf__h{
      font-family:'Cinzel',serif; font-weight:600; font-size:14px; letter-spacing:.05em;
      color:#fff; margin:0 0 16px; padding-bottom:10px; position:relative;
    }
    .avf__h::after{content:""; position:absolute; left:0; bottom:0; width:28px; height:2px; background:var(--avf-gold);}
    .avf__col ul{list-style:none; margin:0; padding:0;}
    .avf__col li{margin-bottom:9px;}
    .avf__col a{
      color:var(--avf-muted); text-decoration:none; font-weight:600; font-size:13.5px;
      transition:color .2s ease,padding-left .2s ease;
    }
    .avf__col a:hover{color:var(--avf-gold); padding-left:5px;}
    .avf__contact li{display:flex; align-items:center; gap:9px; margin-bottom:13px;}
    .avf__contact svg{flex:0 0 auto; color:var(--avf-gold);}
    .avf__contact a{color:var(--avf-text); font-size:13.5px;}
    .avf__hours{margin:4px 0 0; color:var(--avf-muted); font-size:13px;}

    /* ── BOTTOM BAR ── */
    .avf__bottom{
      display:flex; align-items:center; justify-content:space-between; gap:16px;
      flex-wrap:wrap; padding:18px 0 24px; border-top:1px solid var(--avf-line);
    }
    .avf__copy{margin:0; color:var(--avf-muted); font-size:13px;}
    .avf__pay{display:flex; gap:7px; flex-wrap:wrap;}
    .avf__pay span{
      font-size:11px; font-weight:700; letter-spacing:.03em; color:#dfe7ff;
      background:rgba(255,255,255,.08); border:1px solid var(--avf-line);
      padding:5px 10px; border-radius:5px;
    }

    /* ── FOCUS ── */
    .avf a:focus-visible{outline:2px solid var(--avf-gold); outline-offset:3px; border-radius:4px;}

    /* ── TABLET (769px – 1024px) ── */
    @media (min-width:769px) and (max-width:1024px){
      .avf__inner{padding:44px 28px 0;}
      .avf__top{grid-template-columns:55% 41%; gap:4%;}
      .avf__cols{grid-template-columns:repeat(2,1fr); gap:28px; padding:36px 0;}
      .avf__cta-title{font-size:17px;}
      .avf__findus{grid-template-columns:1fr 240px; gap:20px;}
    }

    /* ── SMALL TABLET / LARGE PHONE (481px – 768px) ── */
    @media (max-width:768px){
      .avf__inner{padding:40px 20px 0;}
      .avf{font-size:14px;}

      /* Top: brand full width, then CTA card full width */
      .avf__top{grid-template-columns:1fr; gap:28px; padding-bottom:32px;}

      /* 2-column link grid on tablet portrait */
      .avf__cols{grid-template-columns:repeat(2,1fr); gap:24px 28px; padding:32px 0;}

      .avf__cta{padding:18px 20px;}
      .avf__cta-title{font-size:16px;}
      .avf__cta-text{font-size:13px;}
      .avf__cta-btn{padding:10px 16px; font-size:13px;}

      .avf__h{font-size:13px; margin-bottom:13px;}
      .avf__col a,.avf__contact a{font-size:13px;}
      .avf__col li{margin-bottom:8px;}

      /* Find Us stacks */
      .avf__findus{grid-template-columns:1fr; gap:14px; padding:20px 0;}
      .avf__map iframe{height:120px;}
    }

    /* ── MOBILE (≤ 480px) ── */
    @media (max-width:480px){
      .avf__inner{padding:32px 16px 0;}
      .avf{font-size:13px;}

      .avf__top{gap:22px; padding-bottom:28px;}
      .avf__tagline{font-size:12.5px; margin:0 0 11px;}
      .avf__addr{font-size:12px;}
      .avf__social a{width:34px; height:34px;}

      .avf__cta{padding:16px 18px; border-radius:12px;}
      .avf__cta-eyebrow{font-size:10px;}
      .avf__cta-title{font-size:15px; margin:4px 0 6px;}
      .avf__cta-text{font-size:12px; margin-bottom:13px;}
      .avf__cta-btn{width:100%; justify-content:center; padding:12px 14px; font-size:14px;}
      .avf__cta-lines{justify-content:center; gap:4px 14px; margin-top:12px;}
      .avf__cta-lines a{font-size:12px;}

      /* Find Us — small on phone */
      .avf__findus{padding:16px 0; gap:10px;}
      .avf__findus-title{font-size:14px;}
      .avf__findus-line,.avf__findus-link{font-size:12px;}
      .avf__map iframe{height:95px;}

      /* 2 columns on mobile (not full-width 1 col — saves space) */
      .avf__cols{grid-template-columns:repeat(2,1fr); gap:20px 16px; padding:28px 0;}
      .avf__h{font-size:12px; letter-spacing:.04em; margin-bottom:11px; padding-bottom:8px;}
      .avf__h::after{width:22px;}
      .avf__col a,.avf__contact a{font-size:11.5px; word-break:break-word;}
      .avf__col li{margin-bottom:7px;}
      .avf__contact li{gap:6px; margin-bottom:10px; align-items:flex-start;}
      .avf__contact svg{margin-top:3px;}
      .avf__hours{font-size:12px;}

      .avf__bottom{flex-direction:column; align-items:flex-start; gap:10px; padding:14px 0 20px;}
      .avf__copy{font-size:12px;}
      .avf__pay span{font-size:10px; padding:4px 8px;}
    }

    /* ── LARGE DESKTOP (≥ 1400px) ── */
    @media (min-width:1400px){
      .avf__inner{padding:60px 48px 0;}
      .avf__top{gap:5%;}
      .avf{font-size:16px;}
      .avf__cta-title{font-size:20px;}
      .avf__col a,.avf__contact a{font-size:14.5px;}
      .avf__h{font-size:15px;}
    }

    @media (prefers-reduced-motion:reduce){.avf *{transition:none !important;}}
  </style>

  <script>
    (function(){var y=document.getElementById('avf-year');if(y){y.textContent=new Date().getFullYear();}})();
  </script>
</section>				</div>
				</div>
				</div>
		
</div><!-- close #app div from header.php -->

<script type="speculationrules">
{"prefetch":[{"source":"document","where":{"and":[{"href_matches":"/*"},{"not":{"href_matches":["/wp-*.php","/wp-admin/*","/assets/uploads/*","/assets/*","/assets/plugins/*","/assets/themes/gofly-main/*","/*\\?(.+)"]}},{"not":{"selector_matches":"a[rel~=\"nofollow\"]"}},{"not":{"selector_matches":".no-prefetch, .no-prefetch a"}}]},"eagerness":"conservative"}]}
</script>
<!-- AVICON TRAVEL - CHRISTMAS & ECLIPSE PROMO POPUP -->
<style>
.avi-seasonal-pop{
  position:fixed;
  inset:0;
  z-index:999999;
  display:none;
  align-items:center;
  justify-content:center;
  padding:18px;
  background:rgba(8,24,45,.62);
  font-family:Poppins,Arial,sans-serif;
}
.avi-seasonal-pop.is-visible{display:flex}
.avi-seasonal-pop *{box-sizing:border-box}
.avi-seasonal-modal{
  position:relative;
  width:min(840px,100%);
  overflow:hidden;
  border-radius:16px;
  background:#fff;
  box-shadow:0 26px 80px rgba(0,0,0,.3);
}
.avi-seasonal-close{
  position:absolute;
  top:12px;
  right:12px;
  z-index:5;
  width:34px;
  height:34px;
  border:0;
  border-radius:50%;
  background:rgba(16,35,61,.9);
  color:#fff;
  font-size:22px;
  line-height:1;
  cursor:pointer;
}
.avi-seasonal-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:18px;
  padding:22px 58px 18px 24px;
  background:#10233d;
}
.avi-seasonal-kicker{
  display:block;
  margin-bottom:5px;
  color:#f6a13a;
  font-size:12px;
  font-weight:900;
  text-transform:uppercase;
  letter-spacing:0;
}
.avi-seasonal-top h2{
  margin:0;
  color:#fff;
  font-size:25px;
  line-height:1.18;
  font-weight:900;
  letter-spacing:0;
}
.avi-seasonal-top p{
  max-width:310px;
  margin:0;
  color:rgba(255,255,255,.78);
  font-size:13px;
  line-height:1.55;
}
.avi-seasonal-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:1px;
  background:#dbe6f2;
}
.avi-seasonal-card{
  display:grid;
  grid-template-rows:180px 1fr;
  min-height:100%;
  background:#fff;
  color:#10233d;
  text-decoration:none !important;
}
.avi-seasonal-media{
  position:relative;
  overflow:hidden;
  background:#dfe8f2;
}
.avi-seasonal-media img{
  width:100%;
  height:100%;
  display:block;
  object-fit:cover;
  transition:transform .4s ease;
}
.avi-seasonal-card:hover .avi-seasonal-media img{transform:scale(1.05)}
.avi-seasonal-tag{
  position:absolute;
  left:12px;
  top:12px;
  padding:6px 10px;
  border-radius:999px;
  background:#f6a13a;
  color:#10233d;
  font-size:11px;
  font-weight:900;
}
.avi-seasonal-body{
  display:flex;
  flex-direction:column;
  padding:18px;
}
.avi-seasonal-body h3{
  margin:0 0 9px;
  color:#10233d;
  font-size:19px;
  line-height:1.25;
  font-weight:900;
  letter-spacing:0;
}
.avi-seasonal-body p{
  margin:0 0 14px;
  color:#5d6b80;
  font-size:13px;
  line-height:1.62;
}
.avi-seasonal-info{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-top:auto;
}
.avi-seasonal-info span{
  display:inline-flex;
  align-items:center;
  min-height:29px;
  padding:6px 10px;
  border-radius:999px;
  background:#f4f8fd;
  color:#123f7a;
  font-size:12px;
  font-weight:900;
}
.avi-seasonal-cta{
  display:flex;
  align-items:center;
  justify-content:center;
  min-height:42px;
  margin-top:14px;
  border-radius:8px;
  background:#123f7a;
  color:#fff;
  font-size:13px;
  font-weight:900;
}
.avi-seasonal-card:first-child .avi-seasonal-cta{background:#f6a13a;color:#10233d}
@media(max-width:720px){
  .avi-seasonal-pop{
    align-items:flex-end;
    padding:10px;
  }
  .avi-seasonal-modal{
    width:100%;
    max-height:88vh;
    overflow:auto;
    border-radius:16px 16px 0 0;
  }
  .avi-seasonal-close{
    top:10px;
    right:10px;
    width:32px;
    height:32px;
  }
  .avi-seasonal-top{
    display:block;
    padding:18px 52px 14px 16px;
  }
  .avi-seasonal-top h2{
    font-size:20px;
  }
  .avi-seasonal-top p{
    display:none;
  }
  .avi-seasonal-grid{
    grid-template-columns:1fr;
  }
  .avi-seasonal-card{
    grid-template-columns:118px minmax(0,1fr);
    grid-template-rows:auto;
  }
  .avi-seasonal-media{
    min-height:150px;
  }
  .avi-seasonal-tag{
    left:8px;
    top:8px;
    padding:5px 8px;
    font-size:10px;
  }
  .avi-seasonal-body{
    padding:13px;
  }
  .avi-seasonal-body h3{
    font-size:15px;
    margin-bottom:6px;
  }
  .avi-seasonal-body p{
    display:none;
  }
  .avi-seasonal-info{
    gap:6px;
  }
  .avi-seasonal-info span{
    min-height:25px;
    padding:5px 8px;
    font-size:10px;
  }
  .avi-seasonal-cta{
    min-height:34px;
    margin-top:10px;
    font-size:11px;
  }
}
</style>

<div class="avi-seasonal-pop" id="aviSeasonalPop" role="dialog" aria-modal="true" aria-labelledby="aviSeasonalTitle">
  <div class="avi-seasonal-modal">
    <button class="avi-seasonal-close" type="button" aria-label="Close popup">&times;</button>
    <div class="avi-seasonal-top">
      <div>
        <span class="avi-seasonal-kicker">Limited Egypt Offers</span>
        <h2 id="aviSeasonalTitle">Seasonal Nile Cruise Deals</h2>
      </div>
      <p>Christmas holidays and the rare Egypt Total Solar Eclipse 2027 experience.</p>
    </div>

    <div class="avi-seasonal-grid">
      <a class="avi-seasonal-card" href="/packages/4-days-christmas-new-year-nile-cruise/">
        <div class="avi-seasonal-media">
          <span class="avi-seasonal-tag">Christmas</span>
          <img src="/assets/uploads/2026/05/New-Year-2026.png" alt="Christmas and New Year Nile Cruise Egypt">
        </div>
        <div class="avi-seasonal-body">
          <h3>4 Days Christmas &amp; New Year Nile Cruise</h3>
          <p>A festive Nile cruise between Aswan and Luxor with guided sightseeing and full-board comfort.</p>
          <div class="avi-seasonal-info"><span>4 Days</span><span>From $360</span></div>
          <span class="avi-seasonal-cta">View Offer</span>
        </div>
      </a>

      <a class="avi-seasonal-card" href="/packages/total-solar-eclipse-tour-2027/">
        <div class="avi-seasonal-media">
          <span class="avi-seasonal-tag">Eclipse 2027</span>
          <img src="/assets/uploads/2026/06/Total-Solar-Eclipse-Tour-2027-scaled.png" alt="Total Solar Eclipse Tour 2027 Egypt Nile Cruise">
        </div>
        <div class="avi-seasonal-body">
          <h3>Total Solar Eclipse Tour 2027 Nile Cruise</h3>
          <p>A special Egypt 2027 journey designed around the total solar eclipse and Nile cruise sightseeing.</p>
          <div class="avi-seasonal-info"><span>4 Days</span><span>From $1,200</span></div>
          <span class="avi-seasonal-cta">View Offer</span>
        </div>
      </a>
    </div>
  </div>
</div>

<script>
(function(){
  var popup = document.getElementById('aviSeasonalPop');
  if(!popup) return;
  var closeBtn = popup.querySelector('.avi-seasonal-close');
  var storageKey = 'aviconSeasonalPopupClosedAt';
  var delay = 1400;
  var hideForHours = 24;

  function recentlyClosed(){
    try{
      var last = parseInt(localStorage.getItem(storageKey),10);
      return last && Date.now() - last < hideForHours * 60 * 60 * 1000;
    }catch(e){
      return false;
    }
  }

  function closePopup(){
    popup.classList.remove('is-visible');
    try{ localStorage.setItem(storageKey, String(Date.now())); }catch(e){}
  }

  setTimeout(function(){
    if(!recentlyClosed()) popup.classList.add('is-visible');
  }, delay);

  if(closeBtn) closeBtn.addEventListener('click', closePopup);
  popup.addEventListener('click', function(e){
    if(e.target === popup) closePopup();
  });
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && popup.classList.contains('is-visible')) closePopup();
  });
})();
</script>


<!-- Consent Management powered by Complianz | GDPR/CCPA Cookie Consent https://wordpress.org/plugins/complianz-gdpr -->
<div id="cmplz-cookiebanner-container"><div id="cmplz-cookiebanner-1-optin" class="cmplz-cookiebanner cmplz-hidden banner-1 we-value-your-privacy optin cmplz-bottom-right cmplz-categories-type-view-preferences" aria-modal="true" data-nosnippet="true" role="dialog" aria-live="polite" aria-labelledby="cmplz-header-1-optin" aria-describedby="cmplz-message-1-optin">
	<div class="cmplz-header">
		<div class="cmplz-logo"><a href="/" class="custom-logo-link" rel="home" aria-current="page"><img width="355" height="250" src="/assets/uploads/2026/05/cropped-cropped-Avicon-Travel-1-1.png.webp" class="custom-logo" alt="Avicon Travel" decoding="async" srcset="/assets/uploads/2026/05/cropped-cropped-Avicon-Travel-1-1.png.webp 355w, /assets/uploads/2026/05/cropped-cropped-Avicon-Travel-1-1.png-300x211.webp 300w" sizes="(max-width: 355px) 100vw, 355px" /></a></div>
		<div class="cmplz-title" id="cmplz-header-1-optin">We Value Your Privacy</div>
		<div class="cmplz-close" tabindex="0" role="button" aria-label="Close dialog">
			<svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="times" class="svg-inline--fa fa-times fa-w-11" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 352 512"><path fill="currentColor" d="M242.72 256l100.07-100.07c12.28-12.28 12.28-32.19 0-44.48l-22.24-22.24c-12.28-12.28-32.19-12.28-44.48 0L176 189.28 75.93 89.21c-12.28-12.28-32.19-12.28-44.48 0L9.21 111.45c-12.28 12.28-12.28 32.19 0 44.48L109.28 256 9.21 356.07c-12.28 12.28-12.28 32.19 0 44.48l22.24 22.24c12.28 12.28 32.2 12.28 44.48 0L176 322.72l100.07 100.07c12.28 12.28 32.2 12.28 44.48 0l22.24-22.24c12.28-12.28 12.28-32.19 0-44.48L242.72 256z"></path></svg>
		</div>
	</div>

	<div class="cmplz-divider cmplz-divider-header"></div>
	<div class="cmplz-body">
		<div class="cmplz-message" id="cmplz-message-1-optin"><p>Avicon Travel uses cookies to enhance your browsing experience&nbsp;<br>and help us improve our services. You can choose which cookies&nbsp;<br>to accept below. For more information, please read our&nbsp;<br>Privacy Policy and Cookie Policy.</p></div>
		<!-- categories start -->
		<div class="cmplz-categories">
			<div class="cmplz-category cmplz-functional">
				<div class="cmplz-category-header">
					<span class="cmplz-category-title" id="cmplz-title-functional-1-optin">Essential</span>
					<span class='cmplz-always-active'>
						<span class="cmplz-banner-checkbox">
							<input type="checkbox"
									id="cmplz-functional-optin"
									data-category="cmplz_functional"
									class="cmplz-consent-checkbox cmplz-functional"
									size="40"
									value="1"/>
							<label class="cmplz-label" for="cmplz-functional-optin"><span class="screen-reader-text">Essential</span></label>
						</span>
						Always active					</span>
					<button class="cmplz-category-toggle"
							aria-expanded="false"
							aria-controls="cmplz-desc-functional-1-optin"
							aria-labelledby="cmplz-title-functional-1-optin">
						<span class="cmplz-icon cmplz-open">
							<svg aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" height="18"><path d="M224 416c-8.188 0-16.38-3.125-22.62-9.375l-192-192c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L224 338.8l169.4-169.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-192 192C240.4 412.9 232.2 416 224 416z"/></svg>
						</span>
					</button>
				</div>
				<div class="cmplz-description" id="cmplz-desc-functional-1-optin" hidden>
					<span class="cmplz-description-functional">These cookies are required for the website to function properly, including booking forms and WhatsApp contact features.</span>
				</div>
			</div>

			<div class="cmplz-category cmplz-preferences">
				<div class="cmplz-category-header">
					<span class="cmplz-category-title" id="cmplz-title-preferences-1-optin">Preferences</span>
					<span class="cmplz-banner-checkbox">
						<input type="checkbox"
								id="cmplz-preferences-optin"
								data-category="cmplz_preferences"
								class="cmplz-consent-checkbox cmplz-preferences"
								size="40"
								value="1"/>
						<label class="cmplz-label" for="cmplz-preferences-optin"><span class="screen-reader-text">Preferences</span></label>
					</span>
					<button class="cmplz-category-toggle"
							aria-expanded="false"
							aria-controls="cmplz-desc-preferences-1-optin"
							aria-labelledby="cmplz-title-preferences-1-optin">
						<span class="cmplz-icon cmplz-open">
							<svg aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" height="18"><path d="M224 416c-8.188 0-16.38-3.125-22.62-9.375l-192-192c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L224 338.8l169.4-169.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-192 192C240.4 412.9 232.2 416 224 416z"/></svg>
						</span>
					</button>
				</div>
				<div class="cmplz-description" id="cmplz-desc-preferences-1-optin" hidden>
					<span class="cmplz-description-preferences">The technical storage or access is necessary for the legitimate purpose of storing preferences that are not requested by the subscriber or user.</span>
				</div>
			</div>

			<div class="cmplz-category cmplz-statistics">
				<div class="cmplz-category-header">
					<span class="cmplz-category-title" id="cmplz-title-statistics-1-optin">Analytics</span>
					<span class="cmplz-banner-checkbox">
						<input type="checkbox"
								id="cmplz-statistics-optin"
								data-category="cmplz_statistics"
								class="cmplz-consent-checkbox cmplz-statistics"
								size="40"
								value="1"/>
						<label class="cmplz-label" for="cmplz-statistics-optin"><span class="screen-reader-text">Analytics</span></label>
					</span>
					<button class="cmplz-category-toggle"
							aria-expanded="false"
							aria-controls="cmplz-desc-statistics-1-optin"
							aria-labelledby="cmplz-title-statistics-1-optin">
						<span class="cmplz-icon cmplz-open">
							<svg aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" height="18"><path d="M224 416c-8.188 0-16.38-3.125-22.62-9.375l-192-192c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L224 338.8l169.4-169.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-192 192C240.4 412.9 232.2 416 224 416z"/></svg>
						</span>
					</button>
				</div>
				<div class="cmplz-description" id="cmplz-desc-statistics-1-optin" hidden>
					<span class="cmplz-description-statistics">The technical storage or access that is used exclusively for statistical purposes.</span>
					<span class="cmplz-description-statistics-anonymous">These cookies help us understand how visitors interact with our website, so we can improve your experience. All data is anonymous.</span>
				</div>
			</div>

			<div class="cmplz-category cmplz-marketing">
				<div class="cmplz-category-header">
					<span class="cmplz-category-title" id="cmplz-title-marketing-1-optin">Marketing</span>
					<span class="cmplz-banner-checkbox">
						<input type="checkbox"
								id="cmplz-marketing-optin"
								data-category="cmplz_marketing"
								class="cmplz-consent-checkbox cmplz-marketing"
								size="40"
								value="1"/>
						<label class="cmplz-label" for="cmplz-marketing-optin"><span class="screen-reader-text">Marketing</span></label>
					</span>
					<button class="cmplz-category-toggle"
							aria-expanded="false"
							aria-controls="cmplz-desc-marketing-1-optin"
							aria-labelledby="cmplz-title-marketing-1-optin">
						<span class="cmplz-icon cmplz-open">
							<svg aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" height="18"><path d="M224 416c-8.188 0-16.38-3.125-22.62-9.375l-192-192c-12.5-12.5-12.5-32.75 0-45.25s32.75-12.5 45.25 0L224 338.8l169.4-169.4c12.5-12.5 32.75-12.5 45.25 0s12.5 32.75 0 45.25l-192 192C240.4 412.9 232.2 416 224 416z"/></svg>
						</span>
					</button>
				</div>
				<div class="cmplz-description" id="cmplz-desc-marketing-1-optin" hidden>
					<span class="cmplz-description-marketing">These cookies allow us to show you relevant travel offers and measure the effectiveness of our campaigns.</span>
				</div>
			</div>
		</div><!-- categories end -->
			</div>

	<div class="cmplz-links cmplz-information">
		<ul>
			<li><a class="cmplz-link cmplz-manage-options cookie-statement" href="#" data-relative_url="#cmplz-manage-consent-container">Manage options</a></li>
			<li><a class="cmplz-link cmplz-manage-third-parties cookie-statement" href="#" data-relative_url="#cmplz-cookies-overview">Manage services</a></li>
			<li><a class="cmplz-link cmplz-manage-vendors tcf cookie-statement" href="#" data-relative_url="#cmplz-tcf-wrapper">Manage {vendor_count} vendors</a></li>
			<li><a class="cmplz-link cmplz-external cmplz-read-more-purposes tcf" target="_blank" rel="noopener noreferrer nofollow" href="https://cookiedatabase.org/tcf/purposes/" aria-label="Read more about TCF purposes on Cookie Database">Read more about these purposes</a></li>
		</ul>
			</div>

	<div class="cmplz-divider cmplz-footer"></div>

	<div class="cmplz-buttons">
		<button class="cmplz-btn cmplz-accept">Accept All</button>
		<button class="cmplz-btn cmplz-deny">Deny</button>
		<button class="cmplz-btn cmplz-view-preferences">Customize</button>
		<button class="cmplz-btn cmplz-save-preferences">Save My Choices</button>
		<a class="cmplz-btn cmplz-manage-options tcf cookie-statement" href="#" data-relative_url="#cmplz-manage-consent-container">Customize</a>
			</div>


	<div class="cmplz-documents cmplz-links">
		<ul>
			<li><a class="cmplz-link cookie-statement" href="#" data-relative_url="">{title}</a></li>
			<li><a class="cmplz-link privacy-statement" href="#" data-relative_url="">{title}</a></li>
			<li><a class="cmplz-link impressum" href="#" data-relative_url="">{title}</a></li>
		</ul>
			</div>
</div>
</div>
					<div id="cmplz-manage-consent" data-nosnippet="true"><button class="cmplz-btn cmplz-hidden cmplz-manage-consent manage-consent-1" aria-haspopup="dialog" aria-controls="cmplz-cookiebanner-1-optin">Manage Preferences</button>

</div>			<script>
				const lazyloadRunObserver = () => {
					const lazyloadBackgrounds = document.querySelectorAll( `.e-con.e-parent:not(.e-lazyloaded)` );
					const lazyloadBackgroundObserver = new IntersectionObserver( ( entries ) => {
						entries.forEach( ( entry ) => {
							if ( entry.isIntersecting ) {
								let lazyloadBackground = entry.target;
								if( lazyloadBackground ) {
									lazyloadBackground.classList.add( 'e-lazyloaded' );
								}
								lazyloadBackgroundObserver.unobserve( entry.target );
							}
						});
					}, { rootMargin: '200px 0px 200px 0px' } );
					lazyloadBackgrounds.forEach( ( lazyloadBackground ) => {
						lazyloadBackgroundObserver.observe( lazyloadBackground );
					} );
				};
				const events = [
					'DOMContentLoaded',
					'elementor/lazyload/observe',
				];
				events.forEach( ( event ) => {
					document.addEventListener( event, lazyloadRunObserver );
				} );
			</script>
				<script type='text/javascript'>
		(function () {
			var c = document.body.className;
			c = c.replace(/woocommerce-no-js/, 'woocommerce-js');
			document.body.className = c;
		})();
	</script>
	<link rel='stylesheet' id='wc-blocks-style-css' href='/assets/plugins/woocommerce/assets/client/blocks/wc-blocks.css?ver=wc-10.8.1' type='text/css' media='all' />
<link rel='stylesheet' id='elementor-post-10296-css' href='/assets/uploads/elementor/css/post-10296.css?ver=1788475172' type='text/css' media='all' />
<script type="text/javascript" src="/assets/core/js/dist/hooks.min.js?ver=dd5603f07f9220ed27f1" id="wp-hooks-js"></script>
<script type="text/javascript" src="/assets/core/js/dist/i18n.min.js?ver=c26c3dc7bed366793375" id="wp-i18n-js"></script>
<script type="text/javascript" id="wp-i18n-js-after">
/* <![CDATA[ */
wp.i18n.setLocaleData( { 'text direction\u0004ltr': [ 'ltr' ] } );
//# sourceURL=wp-i18n-js-after
/* ]]> */
</script>
<script type="text/javascript" src="/assets/plugins/review-rating/assets/js/review-rating.js?ver=1.0.0" id="review-rating-script-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/bootstrap.min.js?ver=1778267218" id="bootstrap-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/popper.min.js?ver=1778267218" id="popper-js"></script>
<script type="text/javascript" src="/assets/core/js/dist/vendor/moment.min.js?ver=2.30.1" id="moment-js"></script>
<script type="text/javascript" id="moment-js-after">
/* <![CDATA[ */
moment.updateLocale( 'en_US', {"months":["January","February","March","April","May","June","July","August","September","October","November","December"],"monthsShort":["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],"weekdays":["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"weekdaysShort":["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],"week":{"dow":1},"longDateFormat":{"LT":"g:i a","LTS":null,"L":null,"LL":"F j, Y","LLL":"F j, Y g:i a","LLLL":null}} );
//# sourceURL=moment-js-after
/* ]]> */
</script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/daterangepicker.min.js?ver=1778267218" id="daterangepicker-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/dropzone-min.js?ver=1778267218" id="dropzone-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/swiper-bundle.min.js?ver=1778267218" id="swiper-slider-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/slick.js?ver=1778267218" id="slick-slider-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/waypoints.min.js?ver=1778267218" id="waypoints-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/jquery.counterup.min.js?ver=1778267218" id="counterup-min-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/wow.min.js?ver=1778267218" id="wow-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/range-slider.js?ver=1778267218" id="range-slider-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/gsap.min.js?ver=1778267218" id="gsap-min-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/ScrollTrigger.min.js?ver=1778267218" id="scroll-trigger-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/jquery.nice-select.min.js?ver=1778267218" id="egns-nice-select-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/jquery.fancybox.min.js?ver=1778267218" id="fancybox-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/leaflet.js?ver=1778267218" id="openstreetmap-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/select-dropdown.js?ver=1778267218" id="egns-select-dropdown-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/custom-calendar.js?ver=1778267218" id="custom-calendar-js"></script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/custom-range-calendar.js?ver=1778267218" id="custom-range-calendar-js"></script>
<script type="text/javascript" id="custom-main-js-extra">
/* <![CDATA[ */
var localize_params = {"sticky_header":"1","ajaxurl":"/wp-admin/admin-ajax.php","posts_per_page":"10","author_id":"1","nonce":"ec13dbdbbb","min":"50","max":"2045","exp_min":"10","exp_max":"666","hotel_min":"39","hotel_max":"300","layout":"","symbol":"$"};
//# sourceURL=custom-main-js-extra
/* ]]> */
</script>
<script type="text/javascript" src="/assets/themes/gofly-main/assets/js/custom.js?ver=1778267218" id="custom-main-js"></script>
<script type="text/javascript" src="/assets/plugins/elementor/assets/js/webpack.runtime.min.js?ver=4.1.4" id="elementor-webpack-runtime-js"></script>
<script type="text/javascript" src="/assets/plugins/elementor/assets/js/frontend-modules.min.js?ver=4.1.4" id="elementor-frontend-modules-js"></script>
<script type="text/javascript" src="/assets/core/js/jquery/ui/core.min.js?ver=1.13.3" id="jquery-ui-core-js"></script>
<script type="text/javascript" id="elementor-frontend-js-before">
/* <![CDATA[ */
var elementorFrontendConfig = {"environmentMode":{"edit":false,"wpPreview":false,"isScriptDebug":false},"i18n":{"shareOnFacebook":"Share on Facebook"

