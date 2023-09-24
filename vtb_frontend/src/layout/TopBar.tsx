import {defineComponent} from "vue";
import applicationLogo from '@/assets/images/logos/vtb_logo.svg'

const TopBar = defineComponent({
    name: 'TopBar',
    setup(){
        return () => (
            <div class='top-bar grid p-1 pt-2'>
                <div class='top-bar-logo col-4 mt-1'>
                    <img src={applicationLogo} />
                </div>
                <div class='top-bar-header col-8 text-right text-xs'>
                    <h2 class='mb-0'>Банкоматы и офисы</h2>
                </div>
            </div>
        )
    }
})

export default TopBar