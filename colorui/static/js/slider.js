var redval = document.getElementById("red").value;;
var greenval = document.getElementById("green").value;;
var blueval = document.getElementById("blue").value;;
var brightval = document.getElementById("bright").value;;

function showValues() {
    $('#red-value').html(redval);
    $('#green-value').html(greenval);
    $('#blue-value').html(blueval);
    $('#bright-value').html(brightval);
}

// Activate the sliders
$('#sliders input').on('input change', function () {
    if (this.id == "red"){
        redval = parseFloat(this.value);
    }
    else if (this.id == "green"){
        greenval = parseFloat(this.value);
    }
    else if (this.id == "blue"){
        blueval = parseFloat(this.value);
    }
    else if (this.id == "bright"){
        brightval = parseFloat(this.value);
    }
    showValues();
});


function updateHidden(){
    document.getElementById("redval").value = redval;
    document.getElementById("greenval").value = greenval;
    document.getElementById("blueval").value = blueval;
    document.getElementById("brightval").value = brightval;
    document.getElementById("colorform").submit();
}    



showValues();

