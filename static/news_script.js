
const inputField = document.getElementById("input-field")

const bar = document.querySelector(".bar")

const mainButton = document.getElementById("main-button")


async function sendNews() {
    mainButton.disabled = true;

    const inputNews = inputField.value
    console.log(inputNews)

    if (inputNews.split(/\s+/).length < 4) {
        inputField.placeholder = "Provide Longer Text"
        inputField.value = ""
        setTimeout(() => {
        inputField.placeholder = "Your News Here"
        }, 3000);
      

    }
    else{


    inputField.style.animation = "blinking 1.5s infinite ease-in-out"
    
    const response = await fetch('http://127.0.0.1:5000/verifyNews', {
        method: 'POST',
        headers: {
    'Content-Type': 'application/json',
    
    },
    body: JSON.stringify({'news': inputNews})
})
    
    const data = await response.json()
    

    percentage = data["prediction"]

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