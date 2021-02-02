---
title: js实现context menu
date: 2021-02-01 21:33:43
categories:
	- js/es/ts
tags:
	- js
---


# 各种变量解释
- clientX
相对于浏览器窗口的X
- clientY
相对于浏览器窗口的Y
- offsetX
相对于触发事件元素的X
- offsetY
相对于触发事件元素的Y
- offsetWidth
元素宽度（包括边框）
- offsetHeight
元素高度（包括边框）



# 代码

## JS
```javascript
function ContentMenu(parent) {
    this.menus = []
    const add = (name, handler) => {
        this.menus.push({
            name,
            handler,
        })
    }
    const removeWrapper = () => {
        if (this.wrapper) {
            document.body.removeChild(this.wrapper)
            this.wrapper = null
        }
    }
    const createWrapper = () => {
        const wrapper = document.createElement('ul')
        wrapper.id = 'cm-' + new Date().getTime()
        wrapper.className = 'cm-wrapper'
        wrapper.style.opacity = '0'
        for (let { name, handler } of this.menus) {
            let menu = document.createElement('li');
            menu.addEventListener('click', () => {
                removeWrapper()
                handler.call(this.menus)
            }, false)
            menu.innerText = name
            wrapper.appendChild(menu)
        }
        return wrapper
    }
    parent.oncontextmenu = (event) => {
        event.preventDefault()
        let { clientX, clientY, offsetX, offsetY } = event
        // 创建content wrapper
        const wrapper = createWrapper()
        // 因为wrapper为fixed所以可以直接设置left和top为clientX和clientY
        wrapper.style.left = clientX + 'px'
        wrapper.style.top = clientY + 'px'
        // 删除原有元素
        removeWrapper()
        // 添加到body
        document.body.appendChild(wrapper)
        this.wrapper = wrapper
        // 处理右边界，如果元素内X偏移+本身context宽度大于元素本身宽度
        if (offsetX + wrapper.offsetWidth > parent.offsetWidth) {
            wrapper.style.left = (clientX - wrapper.offsetWidth) + 'px'
        }
        // 处理下边界，如果元素内Y偏移+本身context高度大于元素本身高度
        if (offsetY + wrapper.offsetHeight > parent.offsetHeight) {
            wrapper.style.top = (clientY - wrapper.offsetHeight) + 'px'
        }
        // 因为wrapper的offsetHeight只有在渲染过才能取到，所以在创建时设置成透明
        // 待所有属性都计算完成再显示
        wrapper.style.opacity = '1'
    }
    return {
        add,
    }
}
const cm = new ContentMenu(document.getElementById('xxx'))
cm.add('create', () => alert('create'))
cm.add('update', () => alert('update'))
cm.add('delete', () => alert('delete'))
```

## CSS
```css
#xxx {
    padding: 40px 30px 20px 10px;
    width: 600px;
    height: 400px;
    border: 1px solid #f00;
    position: fixed;
    left: 200px;
    top: 100px;
}
.cm-wrapper {
    list-style: none;
    margin-block: 0;
    padding-inline: 0;
    width: 120px;
    padding: 6px;
    background-color: #eee;
    border-radius: 3px;
    color: #333;
    position: fixed;
}
.cm-wrapper li {
    position: relative;
    padding: 3px 6px;
    border-radius: 3px;
    cursor: pointer;
}
.cm-wrapper li:hover {
    background-color: #69c;
    color: #fff;
}
```

