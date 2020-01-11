var colorPicker = new iro.ColorPicker('#color-picker-container', {
    width: 300,
    layout: [
        { component: iro.ui.Wheel, options: {} }
    ]
});
var brightnessSlider = new iro.ColorPicker('#brightness-slider-container', {
    width: 300,
    layout: [
        { component: iro.ui.Slider, options: {} }
    ],
    color: "rgb(127, 127, 127)"
});

var currentlyChangingColor,
    currentlyChangingBrightness = false;

$(document).ready(function() {
    console.log("ready!");

    // on change of color on color wheel...

    function onColorChange() {
        if (currentlyChangingColor) return;
        currentlyChangingColor = true;

        // grab values
        var value = colorPicker.color.hexString;
        console.log("the color has changed: " + value)

        $.ajax({
            type: "POST",
            url: "/solidcolor",
            data: { 'color': value },
            success: function(results) {
                //reenable event handler now that processing is complete
                currentlyChangingColor = false;
                console.log("color change success");
            },
            error: function(error) {
                console.log(error)
            }
        });
    }

    colorPicker.on('color:change', onColorChange);


    function onBrightnessChange() {
        if (currentlyChangingBrightness) return;
        currentlyChangingBrightness = true;

        // grab values
        var value = brightnessSlider.color.hsl.l;
        console.log("the brightness has changed: " + value + "%")

        $.ajax({
            type: "POST",
            url: "/brightnesschange",
            data: { 'brightness': value },
            success: function(results) {
                //reenable event handler now that processing is complete
                currentlyChangingBrightness = false;
                console.log("brightness change success");
            },
            error: function(error) {
                console.log(error)
            }
        });
    }

    brightnessSlider.on('color:change', onBrightnessChange);

    $("#clearbtn").click(() => {
        $.ajax({
            type: "POST",
            url: "/solidcolor",
            data: { 'color': '#000000' },
            success: function(results) {
                console.log("clear success");
            },
            error: function(error) {
                console.log(error);
                alert("An error has occured: " + error);
            }
        });
    })

    $("#rainbowbtn").click(() => {
        $.ajax({
            type: "POST",
            url: "/pattern",
            data: { 'pattern': 'rainbow' },
            success: function(results) {
                console.log("rainbow success");
            },
            error: function(error) {
                console.log(error);
                alert("An error has occured: " + error);
            }
        });
    })

    $("#sparklebtn").click(() => {
        $.ajax({
            type: "POST",
            url: "/pattern",
            data: { 'pattern': 'sparkle' },
            success: function(results) {
                console.log("sparkle success");
            },
            error: function(error) {
                console.log(error);
                alert("An error has occured: " + error);
            }
        });
    })

});