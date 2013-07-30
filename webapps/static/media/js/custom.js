$(document).ready(function(e) {
   
    
	$('.legislature .legis-link').click(function() {
		$('.legislature ul').toggle();
		return false;
		});
	$('.legislature ul li a').click(function(){
		$('.legislature .legis-link').hide();
		$('.legislature .legis-link').text($(this).text()).show();
		return false;
		});
	$('.most-target .target-drop li a').click(function(){
		$('.most-target .target-link').text($(this).text()).show();
		$(this).parents('.target-drop').hide();
		var sortby = $(this).text();
		var politician = $('#unique').attr('class');
		$('#open-listing-box').load("/load/lettersort/?politician="+politician+"&sortby="+sortby+"");
		return false;

		return false;
		});
		
	$('.promise-txtbx p').click(function() {
		$('.promise-txtbx input[type="text"]').toggle();
		});
	$('.dropComment,.dropComment1').hide();
    $('.controversial, .commentTop').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropComment, .dropComment1').toggle();

        return false;
    });
    $('.dropPanel1').hide();
    $('.dropPanel1profile').hide();
    $(' .mgnifire1, .mgnifire1 .politics').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropPanel1profile').toggle();
       return false;
    });
	$('.dropPanel1 .contentDrop li a').click(function(){
		$('.mgnifire1 .politic .first').text($(this).text());
		$(this).parents().find('.dropPanel1').toggle();
		var politicians = $(this).text();
		if (politicians == 'My Politicians'){
$("#congress").hide();
$("#state").hide();			
$("#mine").show();

			}
		else{
			if(politicians == 'State Legislature'){
			$("#congress").hide();
$("#mine").hide();
$("#state").show();
			}	
		}
		$("#"+politicians).hide();
		});
	$('.dropPanel1profile .contentDrop li a').click(function(){

		$('.mgnifire1 .politic .first').text($(this).text());
		$(this).parents().find('.dropPanel1profile').toggle();
		var politicians = $(this).text();

		if (politicians == 'My Politicians'){
			politicians = 'mine';
			}
		else{
			if(politicians == 'State Legislature'){
			politicians = 'state';
			}	
		}
		$('.bxslider7').load('/load/polilist/?politicians='+politicians+'');
		});
	$('.dropPanel .contentDrop li a').click(function(){
		$(this).parents().find('.state').removeAttr('id');
		$(this).parents().find('.state').attr('id',$(this).attr('class'));
		$(this).parents().find('.dropPanel').toggle();
		
		});
	$('.dropPanel4 .contentDrop li a').click(function(){
		$(this).parents().find('.state1').removeAttr('id');
		$(this).parents().find('.state1').attr('id',$(this).attr('class'));
		$(this).parents().find('.dropPanel4').toggle();
		
		});
	$('.mgnifire2 .magnify2-drop .contentDrop li a').click(function(){
		$('.mgnifire2 h4').text($(this).text());
		});
	
    $('.dropPanel2').hide();
    $(' .mgnifire2').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropPanel2').toggle();
		return false;
    });
    $('.dropPanel3').hide();
    $(' .cont').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropPanel3').toggle();
        return false;
    });
    /*$('.js1').hide();
    $('.contentDrop li.last').click(function(){
        $('.js1').addClass('active');
    });*/
    $('.dropPanel2').hide();
    $('.cont2').click(function(){
        $(this).toggleClass('active');
        $(this).parents().find('.dropPanel2').toggle();
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
	$('.dropPanel4').hide();
    $('.congressDrop_right a, .congressDrop_right h4').click(function(){
        $(this).siblings('.dropPanel').toggle();
	
       return false;
    });	
    $('.congressDrop_right a, .congressDrop_right h4').click(function(){
        $(this).siblings('.dropPanel4').toggle();
	
       return false;
    });	
	$('.target-drop').hide();
	$('.target-link').click(function(){
		$(this).siblings('.target-drop').toggle();
		return false;
		});
	$('.leftsearch_box').hide();
    $('.search-ico').click(function(){
        $(this).siblings('form').children('.leftsearch_box').toggle();
		return false;
    });
	$('.search_box').hide();
    $('nav .search').click(function(){
        $(this).parents('nav').find('.search_box').toggle();
		return false;
    });
	$('.search_politicians .search').click(function(){
        $(this).parents('.politician_container').children('.search_box').toggle();
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
	   var issue = $(this).attr('class');
	   var politician = $('#unique').attr('class');
	if(politician == 'None'){
	   $('#open-letter-box').load("/load/letterbox/issue/?issue="+issue+"");
	   return false;
}
	else{
		$('#open-letter-box').load("/load/letterbox/politician/?target=requested&politician="+politician+"&issue="+issue+"");
	   return false;
		}
	});	


$('.response-issues-list li a').mouseenter(function(){
	   $(this).parent('li').addClass('over');
	   });
	$('.response-issues-list li a').mouseleave(function(){	   
	   $(this).parent('li').removeClass('over');
	});
   	$('.response-issues-list li a').click(function(){
		$('.issues-list li').removeClass('active');
	   $(this).parent('li').addClass('active');
	   var issue = $(this).attr('class');
	   var politician = $('#unique').attr('class');
	
		$('#response-open-letter-box').load("/load/letterbox/politician/?target=responded&politician="+politician+"&issue="+issue+"");
	   return false;
		
	});	

	
	$('.commentbox, .replyComment').hide();
	$('.reply-link').click(function(){
		
		$(this).parents('.commentLink').find('.commentbox, .replyComment').toggle();
		return false;
	});
	$('.reply').click(function(){
	       $(this).toggleClass('active');
		$(this).parents('.commentLink').find('.replyComment').toggle();
		return false;
	});
	$('.open-listing > li:odd').css('background-color','#f6ece2');
	
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
		$(this).siblings('input').toggle();
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
		$(this).siblings('ul').toggle();
		return false;
		});

	$('.messageSocial').click(function(){
		$("#message ul").toggle();
return false;
});

	/*
$('.drop-sec ul li a').click(function(){
		var reasons = [];
		var other = '';
		var comment_id = '';
		$(this).parents().find(':checked').each(function(i){
		if(i == 0){
			comment_id = $(this).attr('class');
			alert(comment_id);
		}
		if($(this).val()=='other'){
			other = $("#other-"+comment_id+"").val();
			alert(other);
		}
		});
		return false;
		});
*/
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
	
	
});
