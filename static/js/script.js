$(document).ready(function () {
    var o = document.getElementById('ad-detect');
    var ad_visible = o && (o.style.display != 'none') && (o.width * o.height);
    setTimeout(function () {$('body').fadeIn(400);}, 100);
    if (ad_visible === 0) {
      setTimeout(function () {$('.modal-window').fadeIn();}, 400);
      $('.all-content').css('opacity', '0.05');
      $('.modal-window').css('display', 'flex');
      $('body').css('overflow', 'hidden');
    }
    $(document).click(function() {
        $('.modal-window').hide();
        $('.all-content').css('opacity', '1');
        $('body').css('overflow', 'scroll');
    });
  	$('.short_url').click( function () {
  		navigator.clipboard.writeText($('.short_url').text())
    			.then(() => {
  				$('.short_url').css('color', 'red');
  				$('.copy').text('Скопировано');
  				$('.copy').css('color', 'red');})
        });

    /*$('.api-nav').click(function (event) {
        event.preventDefault();
        setTimeout(function() {window.location = "https://warp.fun/api/";}, 100);
    });
    $('.mailing').click(function (event) {
        event.preventDefault();
        setTimeout(function() {window.location = "https://warp.fun/mailing/";}, 100);
    });
    $('.about').click(function (event) {
        event.preventDefault();
        setTimeout(function() {window.location = "https://warp.fun/about/";}, 100);
    });
    $('.main').click(function(event) {
        event.preventDefault();
        setTimeout(function() {window.location = "https://warp.fun/";}, 100);
    });
    $('.get-api-code').click(function(event){
        event.preventDefault();
        setTimeout(function() {window.location = "https://warp.fun/api/get-access-key/";}, 100);
    });*/
    $('.discord').click(function() {
        navigator.clipboard.writeText($('.discord-text').text());
        $('.discord').text('Скопировано');
        $('.discord').css("background-color", "#007bff");
        $('.discord').css("color", "white");
    });
    $(".dev-head-el-docs").click(function () {
  		elementClick = $('.dev-head-el-docs a').attr("href");
  		destination = $(elementClick).offset().top;
  		$("body,html").animate({scrollTop: destination }, 800);
	  });
    $('.gmail').click(function() {
        navigator.clipboard.writeText($('.gmail-text').text());
        $('.gmail').text('Скопировано');
        $('.gmail').css("background-color", "#007bff");
        $('.gmail').css("color", "white");
    });
    $('.btn-get-access-key').hover(function() {
        $('.btn-get-access-key').animate({
            padding: '15px 20px',
            fontSize: '20px',
            borderRadius: '100px',
            borderWidth: '1px'
        })
    });
});
