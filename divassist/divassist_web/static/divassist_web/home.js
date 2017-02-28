$(document).ready(function(){
    var setGreeting = function() {
        var d = new Date();
        var h = d.getHours();
        var word;
        if (h >= 6 && h <= 11) {
            word = "morning";
        } else if (h >= 12 && h <= 17) {
            word = "afternoon";
        } else {
            word = "evening";
        }
        $("#greeting-time").text(word);
    }

    setGreeting();

    $(".second-level-option").hide();

    $(".first-level-option, .second-level-option").hover(
        function() {
            if (!$(this).hasClass("selected")) {
                $(this).animate({
                    "padding-left": "+=1em"
                }, 100);
                $(this).css({
                    "background-color": "#3DB7E4",
                    "color": "#FFFFFF"
                });
            }
        }, 
        function() {
            if (!$(this).hasClass("selected")) {
                $(this).animate({
                    "padding-left": "-=1em"
                }, 150);
                $(this).css({
                    "background-color": "#FFFFFF",
                    "color": "#263238"
                });
            }
        }
    );

    var expandAllSub = function(obj) {
        var cur = obj.next();
        while (cur.hasClass("second-level-option")) {
            cur.show(150);
            cur = cur.next();
        }
    }

    var hideAllSub = function(obj) {
        var cur = obj.next();
        while (cur.hasClass("second-level-option")) {
            cur.hide(200);
            cur = cur.next();
        }
    }

    var removeSelectedProperty = function() {
        $(".selected").animate({"padding-left": "-=1em"}, 150);
        $(".selected").css({
            "color": "#263238",
            "background-color": "#FFFFFF"
        });
        $(".selected").removeClass("selected");
        $(".expanded").removeClass("expanded");
    }

    var executeFunc = function(obj) {
        var func = obj.attr("func");
        if (func === "land") {
            window.location.href = obj.attr("dest");
        } else if (func === "load") {
            var dest = obj.attr("dest");
            console.log(dest);
            $("#load-window").attr("src", dest);
        }
    }

    $(".first-level-option").click(function() {
        if ($(this).attr("func") === "expand") {
            if ($(this).hasClass("expanded")) {
                hideAllSub($(this));
                $(this).removeClass("expanded");
            } else {
                expandAllSub($(this));
                $(this).addClass("expanded");
            }
        } else {
            if (!$(this).hasClass("selected")) {
                removeSelectedProperty();
                $(".second-level-option").hide(200);
                $(this).addClass("selected");
                $(this).css({"background-color": "#263238"});
                executeFunc($(this));
            }
        }
    });

    $(".second-level-option").click(function() {
        if (!$(this).hasClass("selected")) {
            removeSelectedProperty();
            $(this).addClass("selected");
            $(this).css({"background-color": "#263238"});
            executeFunc($(this));
        }   
    });

    var adjustIframeSize = function() {
        var iframeH = $(window).outerHeight() - $("#nav").outerHeight() - $("#footer").outerHeight() - parseInt($("#main-container").css("padding-top")) * 2 - $("#greeting").outerHeight();
        console.log("Height=" + iframeH);
        var iframeW = $("#greeting").outerWidth() - $("#home-nav").outerWidth() - 15;
        console.log("Width=" + iframeW);
        $("iframe").css({
            "height": iframeH.toString() + "px",
            "width": iframeW.toString() + "px"
        });
    }

    adjustIframeSize();

    $(window).resize(function() {
        adjustIframeSize();
    });
});