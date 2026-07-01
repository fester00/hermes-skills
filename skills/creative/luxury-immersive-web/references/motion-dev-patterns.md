# Motion.dev vs GSAP — Quick Decision Reference

## 1-Sentence Rule

**GSAP** = scroll-linked orchestration. **Motion** = component-level declarative life. Coexist, don't compete.

## When to Reach for Motion

Use `npm install motion` (fresh) or upgrade `framer-motion` (existing).

Import: `import { motion, AnimatePresence } from "motion/react"` or `"framer-motion"`. Same API.

**Best for:**
- Component mount/unmount entrance/exit → `AnimatePresence`
- Hover / tap micro-interactions → `whileHover`, `whileTap`
- Drag gestures + throw physics → `drag` prop
- Layout reflow animations → `layout` prop
- Spring physics (bounce, elastic) → `type: "spring"` (native)
- Staggered children → `variants` + `staggerChildren`
- Scroll-triggered simple entrance → `whileInView`

**Not for:**
- Scroll pin, scrub, horizontal scroll → GSAP ScrollTrigger only
- Complex multi-timeline sequencing → GSAP Timeline only

## Patterns Summary

| Pattern | Code Snippet |
|---------|-------------|
| Floating card (CSS 3D) | `<motion.div initial={{opacity:0,y:50,rotateY:-20}} animate={{...}} whileHover={{rotateY:12,translateZ:40}} transition={{type:'spring'}}>` |
| Preloader exit | `<AnimatePresence><motion.div exit={{y:'-100%'}} /></AnimatePresence>` |
| Stagger reveal | `variants={{ hidden:{}, visible:{transition:{staggerChildren:0.1}} }}` |
| While in view | `<motion.div whileInView="visible" viewport={{once:true}}>` |

## Integration Pitfalls

1. **Import path:** `"motion/react"` (v12+) or `"framer-motion"` (v11 legacy). Same exports. The former future-proofs.
2. **Inside CSS 3D:** Use `style={{ transformStyle: 'preserve-3d' }}` on `motion.div`, not Tailwind `className` — Tailwind may purge unused utilities.
3. **Spring inside CSS 3D:** `transition={{ type: 'spring', stiffness: 200, damping: 15 }}` works perfectly on `rotateY`, `rotateX`, `translateZ`.
4. **AnimatePresence key:** Always provide `key` prop on animated child inside `AnimatePresence`. Without it, exit animation won't fire.
5. **GSAP + Motion together:** No conflicts. Init GSAP ScrollTrigger + Lenis as usual. Wrap GSAP-animated elements in Motion only where component-level declarative is cleaner.

## Version History

- `framer-motion@11.3.0` → existing in VIDVIS package.json
- `framer-motion@12.40.0` → latest
- `motion` (npm) → new branding, same codebase
- Import from `"motion/react"` → forward-compatible

## Links

- [motion.dev/docs](https://motion.dev/docs)
- [Framer Motion API](https://www.framer.com/motion/) (legacy branding)
- Skill: `luxury-immersive-web` — full patterns in SKILL.md §0b–0e.
