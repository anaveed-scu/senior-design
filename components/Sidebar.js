import React from 'react';
import Link from 'next/link';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <ul>
        <li><Link href="/">Overview</Link></li>
        <li><Link href="/borrow">Borrow</Link></li>
        <li><Link href="/lend">Lend</Link></li>
        <li><Link href="/account">Account</Link></li>
      </ul>
    </div>
  );
};

export default Sidebar;

