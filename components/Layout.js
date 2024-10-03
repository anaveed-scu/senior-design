// components/Layout.js
import Link from 'next/link';
import styles from './Layout.module.css';

export default function Layout({ children }) {
  return (
    <div className={styles.container}>
      <aside className={styles.sidebar}>
        <nav>
          <ul>
            <li>
              <Link href="/" className={styles.navItem}>Overview</Link>
            </li>
            <li>
              <Link href="/borrow" className={styles.navItem}>Borrow</Link>
            </li>
            <li>
              <Link href="/lend" className={styles.navItem}>Lend</Link>
            </li>
            <li>
              <Link href="/account" className={styles.navItem}>Account</Link>
            </li>
          </ul>
        </nav>
      </aside>
      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
}

