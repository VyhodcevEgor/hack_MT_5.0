import {defineComponent, PropType, ref} from "vue";
import { YandexMap } from "vue-yandex-maps";

type AppMapPropsType = {
    initialPosition: string[],
}

const AppMap = defineComponent({
    name: 'AppMap',
    props: {
        initialPosition: Array as PropType<AppMapPropsType['initialPosition']>
    },
    components: {
        YandexMap,
    },
    setup(props) {
        const {initialPosition} = props
        console.log(initialPosition)
        const mapInitialPosition = ref<number[]>([45.0195555, 41.9002591]);

        const settings = {
            apiKey: '69baf678-987f-4d0c-ac67-89f559e9c253',
            lang: 'ru_RU',
            coordorder: 'latlong',
            enterprise: false,
            version: '2.1'
        }

        return () => (
            <div id='map' class='w-full' style='height: 100vh'>
                {/*Для реализации функционала за основу взяты яндекс карты. Чтобы внешне выглядело красиво были убраны метки
                 и функциональные кнопки яндекса. Это используется исключительно в целях дизайна. Яндекс самостоятельно говорят о том,
                 что любой продукт похожий на их, дает им рекламу, соответственно мы не переманиваем их клиентов и не воруем функционал.
                 Мы используем исключительно оффициальную лицензию, с частичными ограничениями, распространяющаяся бесплатно в общем доступе*/}
                <YandexMap settings={{...settings}} coordinates={mapInitialPosition.value} class="map">
                </YandexMap>
            </div>
        )
    }
})

export default AppMap