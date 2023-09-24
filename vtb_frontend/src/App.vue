<script setup lang="ts">
import TopBar from "@/layout/TopBar.tsx";
import AppMap from "@/layout/AppMap.tsx";
import BottomBar from "@/layout/BottomBar.vue";
import {onBeforeMount, onMounted, ref} from "vue";

const Geolocation = navigator.geolocation;
const initialPosition = ref<number[]>()

const setInitialPosition = (position: any) => {
  initialPosition.value = [position.coords.latitude, position.coords.longitude]
}

const getPositionErrorHandler = (error: any) => {
  console.error(error)
}

onMounted(() => {
  const options = {
    enableHighAccuracy: true,
    timeout: 5000,
    maximumAge: 0
  };

  Geolocation.getCurrentPosition(setInitialPosition, getPositionErrorHandler, options)
})
</script>

<template>
<!--  <TopBar />-->
  <AppMap v-show="initialPosition" :initial-position="initialPosition"/>
  <BottomBar />
</template>

<style scoped>
</style>
