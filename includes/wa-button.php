<?php // floating whatsapp button ?>
<style>
.avi-wa-booking{
  position:fixed;
  left:22px !important;
  right:auto !important;
  bottom:22px;
  z-index:99999;
  display:inline-flex;
  align-items:center;
  gap:10px;
  min-height:56px;
  padding:12px 18px 12px 14px;
  border-radius:999px;
  background:#25d366;
  color:#fff !important;
  font-family:Poppins,Arial,sans-serif;
  font-size:15px;
  font-weight:900;
  text-decoration:none !important;
  box-shadow:0 14px 32px rgba(37,211,102,.38);
  animation:aviWaFloat 2.8s ease-in-out infinite;
}
.avi-wa-booking:before{
  content:"";
  position:absolute;
  inset:-7px;
  border-radius:999px;
  border:2px solid rgba(37,211,102,.38);
  animation:aviWaPulse 1.9s ease-out infinite;
}
.avi-wa-booking i{
  width:34px;
  height:34px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  border-radius:50%;
  background:#fff;
  color:#25d366;
  font-size:21px;
  flex:0 0 auto;
}
.avi-wa-booking span{position:relative;z-index:1;white-space:nowrap}
.avi-wa-booking:hover{transform:translateY(-3px);box-shadow:0 18px 38px rgba(37,211,102,.48)}
@keyframes aviWaPulse{0%{transform:scale(.92);opacity:.75}70%{transform:scale(1.2);opacity:0}100%{transform:scale(1.2);opacity:0}}
@keyframes aviWaFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
@media(max-width:640px){
  .avi-wa-booking{left:16px !important;right:auto !important;bottom:16px;width:54px;height:54px;min-height:54px;padding:0;justify-content:center;gap:0}
  .avi-wa-booking i{width:34px;height:34px;font-size:22px}
  .avi-wa-booking span{display:none}
}
</style>
<a class="avi-wa-booking" href="https://wa.me/201200555600?text=Hello%20Avicon%20Travel%2C%20I%20want%20to%20book%20a%20tour" target="_blank" rel="noopener" aria-label="Book on WhatsApp">
  <i class="fab fa-whatsapp" aria-hidden="true"></i>
  <span>Book on WhatsApp</span>
</a>
