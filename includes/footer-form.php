<?php // tailor-made form footer variant ?>
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
        <div class="avi-info__image-wrap"><img decoding="async" src="/assets/uploads/2026/06/Avicon-Customer-Reviews-Pyramids-Giza.png.webp" alt="Egypt Tour Experience"></div>
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
