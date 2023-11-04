<template>
  <div class="container">
    <div class="status__container">
      <span v-if="status">{{ status }}</span>
    </div>
    <div class="btns">
      <button class="btn green" @click="no_attack_db">Обычный запрос</button>
      <button class="btn red" @click="attack_db">Запрос с атакой</button>
    </div>
  </div>
</template>

<script>

export default {
  name: 'App',
  data() {
    return {
      status: ''
    }
  },
  methods:{
    attack_db(){
      this.status = "Ваш сервер атакован"
    },
    no_attack_db(){
      this.status = "На ваш сервер ушел обычный запрос"
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,400;1,700&display=swap');

body,
html{
  font-family: 'Ubuntu', sans-serif;
  font-size: 45px;
}

.container{
  width: 70%;
  height: 100vh;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 50px;
}

.status__container{
  width: 100%;
  height: 100px;
  display: flex;
  justify-content: center;
}

.btns{
  display: flex;
  gap: 20px;
}

.btn{
  font-size: 35px;
  padding: 10px 20px;
  border-radius: 100px;
}

.green{
  background-color: rgb(6, 255, 6);
}

.red{
  background-color: rgb(157, 2, 2);
  color: blue;
}







/* Reset and base styles  */
* {
	padding: 0px;
	margin: 0px;
	border: none;
}

*,
*::before,
*::after {
	box-sizing: border-box;
}

/* Links */

a, a:link, a:visited  {
    text-decoration: none;
}

a:hover  {
    text-decoration: none;
}

/* Common */

aside, nav, footer, header, section, main {
	display: block;
}

h1, h2, h3, h4, h5, h6, p {
    font-size: inherit;
	font-weight: inherit;
}

ul, ul li {
	list-style: none;
}

img {
	vertical-align: top;
}

img, svg {
	max-width: 100%;
	height: auto;
}

address {
  font-style: normal;
}

/* Form */

input, textarea, button, select {
	font-family: inherit;
    font-size: inherit;
    color: inherit;
    background-color: transparent;
}

input::-ms-clear {
	display: none;
}

button, input[type="submit"] {
    display: inline-block;
    box-shadow: none;
    background-color: transparent;
    background: none;
    cursor: pointer;
}

input:focus, input:active,
button:focus, button:active {
    outline: none;
}

button::-moz-focus-inner {
	padding: 0;
	border: 0;
}

label {
	cursor: pointer;
}

legend {
	display: block;
}

</style>
