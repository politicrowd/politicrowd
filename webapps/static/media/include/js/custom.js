$(document).ready(function(e) {
	/*change*/
	/*$('#propen, .legislature ul').hide();*/
	/*change*/
	$('.legislature .legis-link').click(function() {
		$('.legislature ul').slideToggle();
		return false;
		});
	$('.legislature ul li a').click(function(){
		$('.legislature .legis-link').hide();
		$('.legislature .legis-link').text($(this).text()).show();
		$(this).parents('ul').hide();
		return false;
		});
	$('.most-target .target-drop li a').click(function(){
		$('.most-target .target-link').text($(this).text()).show();
		$(this).parents('.target-drop').hide();
		return false;
		});
	if ($('.target-drop, .dropPanel1, .dropPanel, .legislature ul').show())
	{
		$('body').click(function(){
			$('.target-drop, .dropPanel1, .dropPanel, .legislature ul').hide();
			});
	}
	$('.up_arrow_grey').click(function(){
		$('.thanks').toggle();
		return false;
		});	
                $('.activator').click(function(){
		$('.sideSlide2').toggle();
		return false;
		});
	 
	$('.promise-txtbx p').click(function() {
		$('.promise-txtbx input[type="text"]').slideToggle();
		});
	$('.dropComment,.dropComment1').hide();
    $('.controversial, .commentTop').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropComment, .dropComment1').slideToggle('fast');

        return false;
    });
    $('.dropPanel1').hide();
    $(' .mgnifire1, .mgnifire1 .politics').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropPanel1').slideToggle('fast');
       return false;
    });
	$('.dropPanel1 .contentDrop li a').click(function(){
		$('.mgnifire1 .politic .first').text($(this).text());
		$(this).parents('.dropPanel1').hide();
		});
	$('.dropPanel .contentDrop li a').click(function(){
		$('.mgnifire h4').text($(this).text());
		$(this).parents('.dropPanel').hide();
		});
	$('.mgnifire2 .magnify2-drop .contentDrop li a').click(function(){
		$('.mgnifire2 h4').text($(this).text());
		});
	
    $('.dropPanel2').hide();
    $(' .mgnifire2').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropPanel2').slideToggle('fast');
		return false;
    });
    $('.dropPanel3').hide();
    $(' .cont').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropPanel3').slideToggle('fast');
        return false;
    });
    /*$('.js1').hide();
    $('.contentDrop li.last').click(function(){
        $('.js1').addClass('active');
    });*/
    $('.dropPanel2').hide();
    $('.cont2').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropPanel2').slideToggle('fast');
        return false;
    });
	$('.forgotPop').hide();
	$('.forgot a').click(function(){
		$('.forgotPop').toggle();
		return false;
		});
	/*correct code javascript begins here*/
	/*mobile navigation js goes here*/
	$('.mob-menu span').click(function(){
		$(this).hide();
		$(this).siblings('span').show();
		$('nav').toggle();
		return false;
		});
	$('.dropPanel').hide();
    $('.congressDrop_right a, .congressDrop_right h4').click(function(){
        $(this).siblings('.dropPanel').slideToggle(300);
       return false;
    });	
	$('.target-drop').hide();
	$('.target-link').click(function(){
		$(this).siblings('.target-drop').slideToggle(300);
		return false;
		});
	$('.leftsearch_box').hide();
    $('.search-ico').click(function(){
        $(this).siblings('form').children('.leftsearch_box').slideToggle(300);
		return false;
    });
	$('.search_box').hide();
    $('nav .search').click(function(){
        $(this).parents('nav').find('.search_box').slideToggle(100);
		return false;
    });
	$('.search_politicians .search').click(function(){
        $(this).parents('.politician_container').children('.search_box').slideToggle(100);
		return false;
    });
   	$('.issues-list li a').mouseenter(function(){
	   $(this).parent('li').addClass('over');
	   });
	$('.issues-list li a').mouseleave(function(){	   
	   $(this).parent('li').removeClass('over');
	});
   	$('.issues-list li a').click(function(){
		$('.issues-list li').removeClass('active');
	   $(this).parent('li').addClass('active');
	   return false;
	});	
	$('.reply, .commentbox, .commenttxt, .replyComment').hide();
	$('.reply-link').click(function(){
		$(this).parents('.commentList').children('.reply').toggle();
		$(this).parents('.commentLink').find('.replyComment, .commentbox').show();
		return false;
	});
	$('.reply p').click(function(){
		$(this).parents('.commentLink').find('.replyComment, .commentbox, .commenttxt').show();
		return false;
	});
	$('.open-head ul li a').click(function(){
		$('.open-head ul li').removeClass('active');
		$(this).parent('li').addClass('active');
		return false;
	});
	$('.open-listing > li:odd').css('background-color','#f6ece2');
	$('.ok-btn').click(function(){
		$('.thanks').hide();
		return false;
	});
	 $('.req-pro').click(function(){
		 $(this).siblings('.honk').toggle();
		 return false;
	});
	$('.promise-txtbx a').click(function(){
			$('.promise-txtbx a').removeClass('active');
			$(this).addClass('active');
			return false;
	});
	$('.promise-txtbx.profile input').hide();
	$('.promise-txtbx.profile small').click(function(){
		$(this).siblings('input').slideToggle();
		});
		
	$('.committee-sec').hide().eq(1).show();
	$('.info-sec li').eq(1).addClass('active');						 
	$('.info-sec li a').click(function(){
		$('.info-sec li').removeClass('active');
		$(this).parent().addClass('active');
		var currentTab = $(this).attr('href');
		$('.committee-sec').hide();
		$(currentTab).show();
		return false;
	});
	$('.closeUL').click(function(){
		$(this).siblings('ul').slideToggle(100);
		return false;
		});
	/*change*/
	$('#propen, .legislature ul').hide();
	$('.state-list li').slice(6).hide();
	$('.searchLeft .or a.view-next').click(function(){
		$('.state-list li.js1').show();
		$(this).siblings('a').show();
		});
	$('.searchLeft .or a.view-prev').click(function(){
		$('.state-list li.js1').hide();
		$(this).hide();
		});
	$('.reply-overlay a').click(function(){
		$('.reply-overlay').hide();
		return false;
		});
	$('.upvote_downvote_left .up_arrow_grey').click(function(){
		$(this).addClass('up_arrow_red');
		$('.star-notification').show();
		bxSlider();
		return false;
		});
	$('.upvote_downvote_left .down_arrow_grey').click(function(){
		$(this).addClass('down_arrow_red');
		return false;
		});		
	$('#all-issue').click(function(){
		allissue();
		return false;
		});
			
	function allissue(){
		if($(window).width() < 992){
			$('.issue-left-sec').removeClass('hidden');
			$('.issue-left-sec').addClass('visible');
			$('.issues-list li a').click(function(){
				$('#all-issue').text($(this).text());
				$(this).parents('.issue-left-sec').addClass('hidden');
				return false;
			});
		}	
		else{return false;}
	}
	
	/*change*/
});


