<template>
  <span v-if="status">{{ status }}</span>
  <button style="background-color:green; cursor:pointer" @click="no_attack_db">+</button>
  <button style="background-color:red; cursor:pointer" @click="attack_db">-</button>
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
      this.status = "poka"
    },
    no_attack_db(){
      this.status = "privet"
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
