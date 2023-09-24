<script setup lang="ts">
import {ref} from "vue";

const bottomBarStructure = [
  {name: 'settings', icon: 'settings', class: 'settings-button'},
  {name: 'favorite', icon: 'favorite', class: 'favorite-button'},
  {name: 'map', icon: 'map', class: 'map-button'},
  {name: 'bookmark_added', icon: 'bookmark_added', class: 'bookmark-button'},
  {name: 'time', icon: 'schedule', class: 'time-button'},
]

const currentChapter = ref<string>('');

const getCurrentClass = (chapterName: string) => {
  return currentChapter.value === chapterName ? 'button' : ''
};
</script>

<template>
  <div class="grid bottom">
    <template v-for="chapter in bottomBarStructure">
      <div class="col-2">
        <span class="material-icons-round">{{chapter.icon}}</span>
      </div>
    </template>
  </div>
</template>

<style scoped>
span {
  color: var(--primary-color);
  cursor: pointer;
}
</style>
