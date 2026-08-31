const inputField = document.getElementById("input-field")

const bar = document.querySelector(".bar")

const mainButton = document.getElementById("main-button")


async function sendNews() {
    mainButton.disabled = true;

    const user_input = inputField.value
    

    const pieces = user_input.split(/\s+/)

    const wordsAll = pieces.filter(piece => /\p{L}/u.test(piece))
    const wordsEnglish = pieces.filter(piece => /[a-zA-Z]/u.test(piece))

    

    if (wordsAll.length > wordsEnglish.length) {
        
        inputField.placeholder = "Provide fully English Text"

        inputField.value = ""

        setTimeout(() => {
        inputField.placeholder = "Your Text Here"
        inputField.value = user_input
        }, 3000);

        

    } 

    else if (wordsEnglish.length < 2) {

        inputField.placeholder = "Provide a Complete Text"

        inputField.value = ""

        setTimeout(() => {
        inputField.placeholder = "Your News Here"
        inputField.value = user_input
        }, 3000);


    }

    else{

    inputField.style.animation = "blinking 1.5s infinite ease-in-out"
    
    const response = await fetch('/verifyNews', {
        method: 'POST',
        headers: {
    'Content-Type': 'application/json',
    
    },
    body: JSON.stringify({'user_input': user_input})
    })
    
    const data = await response.json()

    inputField.style.animation = "none"
    
    if (data["error"]){

        inputField.placeholder = data["error"]

        inputField.value = ""

        setTimeout(() => {
        inputField.placeholder = "Your News Here"
        inputField.value = user_input

        }, 3000);

        mainButton.disabled = false;

        return;

    }
    
    const percentage = data["prediction"]
    console.log(percentage)

    inputField.style.animation = "none"

    if (percentage<50){
        bar.style.visibility = 'visible'

        const colorValue = (((100 - percentage)/100) * 255)

        inputField.style.borderColor = `rgb(${colorValue}, 0, 0)`
        inputField.style.boxShadow = `0px 0px 25px rgb(${colorValue}, 0, 0)`

        bar.style.backgroundColor = `rgb(${colorValue}, 0, 0)`      
        bar.style.borderColor = `rgb(${colorValue}, 0, 0)`
        bar.style.boxShadow = `0px 0px 25px rgb(${colorValue}, 0, 0)`

        bar.style.width = `${percentage}%`
    }

    else if (percentage > 50) {
        bar.style.visibility = 'visible'

        const colorValue = (((percentage)/100) * 255)

        inputField.style.borderColor = `rgb(60, ${colorValue}, 0)`
        inputField.style.boxShadow = `0px 0px 25px rgb(60, ${colorValue}, 0)`
        


        bar.style.backgroundColor = `rgb(60, ${colorValue}, 0)`
        bar.style.borderColor = `rgb(60, ${colorValue}, 0)`
        bar.style.boxShadow = `0px 0px 25px rgb(60, ${colorValue}, 0)`

        bar.style.width = `${percentage}%`
        
    } else {
        bar.style.visibility = 'visible'

        inputField.style.borderColor = "white"
        inputField.style.boxShadow = "0px 0px 25px white"

        bar.style.backgroundColor = "white"
        bar.style.borderColor = "white"
        bar.style.boxShadow = "0px 0px 25px white"

        

        bar.style.width = `${percentage}%`
        
    }
    }
    

    mainButton.disabled = false;
    
}