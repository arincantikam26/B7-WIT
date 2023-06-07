// script.js
document.addEventListener('DOMContentLoaded', function() {
    var btnBackToTop = document.getElementById('back-top');
  
    window.onscroll = function() {
      if (document.documentElement.scrollTop > 300) {
        btnBackToTop.style.display = 'block';
      } else {
        btnBackToTop.style.display = 'none';
      }
    };
  
    btnBackToTop.addEventListener('click', function() {
      document.documentElement.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
    
  });
  
  function scrollToTarget() {
    const targetDiv = document.getElementById('section-tittle');
    targetDiv.scrollIntoView({ behavior: 'smooth' });
}

$(document).ready(function(){
  $(".fancybox").fancybox({
        openEffect: "none",
        closeEffect: "none"
    });
    
    $(".zoom").hover(function(){
		
		$(this).addClass('transition');
	}, function(){
        
		$(this).removeClass('transition');
	});
});
    